#requires -Version 7.0

[CmdletBinding()]
param(
    [ValidateSet("All", "STM32", "ESP32")]
    [string]$Target = "All",

    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Debug",

    [string]$CubeIdeHeadlessPath,
    [string]$EspIdfProfilePath,
    [string]$EspPythonPath,
    [string]$IdfPyPath,
    [string]$ArtifactRoot,

    [switch]$RequireClean,
    [switch]$KeepStage
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (Test-Path -LiteralPath "Variable:PSNativeCommandUseErrorActionPreference") {
    $PSNativeCommandUseErrorActionPreference = $false
}

function Resolve-ExistingFile {
    param(
        [string]$RequestedPath,
        [string[]]$Candidates,
        [string]$Description
    )

    if (-not [string]::IsNullOrWhiteSpace($RequestedPath)) {
        $resolvedRequestedPath = [System.IO.Path]::GetFullPath($RequestedPath)
        if (Test-Path -LiteralPath $resolvedRequestedPath -PathType Leaf) {
            return $resolvedRequestedPath
        }

        throw "$Description was not found at the requested path: $resolvedRequestedPath"
    }

    foreach ($candidate in $Candidates) {
        if ([string]::IsNullOrWhiteSpace($candidate)) {
            continue
        }

        $resolvedCandidate = [System.IO.Path]::GetFullPath($candidate)
        if (Test-Path -LiteralPath $resolvedCandidate -PathType Leaf) {
            return $resolvedCandidate
        }
    }

    throw "$Description was not found. Pass its path explicitly."
}

function Invoke-LoggedNativeCommand {
    param(
        [string]$FilePath,
        [string[]]$ArgumentList,
        [string]$LogPath,
        [string]$Description
    )

    Write-Host "`n==> $Description"
    $output = & $FilePath @ArgumentList 2>&1
    $exitCode = $LASTEXITCODE
    $output | Tee-Object -FilePath $LogPath | Out-Host

    if ($exitCode -ne 0) {
        throw "$Description failed with exit code $exitCode. Log: $LogPath"
    }
}

function Copy-IsolatedTree {
    param(
        [string]$Source,
        [string]$Destination,
        [string[]]$ExcludedDirectories,
        [string]$LogPath
    )

    $null = New-Item -ItemType Directory -Path $Destination -Force

    $robocopyArguments = @(
        $Source,
        $Destination,
        "/E",
        "/COPY:DAT",
        "/DCOPY:DAT",
        "/R:2",
        "/W:1",
        "/XJ",
        "/NFL",
        "/NDL",
        "/NP",
        "/XD"
    ) + $ExcludedDirectories

    $output = & robocopy.exe @robocopyArguments 2>&1
    $exitCode = $LASTEXITCODE
    $output | Tee-Object -FilePath $LogPath | Out-Host

    # Robocopy uses 0 through 7 for success or non-fatal copy differences.
    if ($exitCode -ge 8) {
        throw "Isolated copy failed with Robocopy exit code $exitCode. Log: $LogPath"
    }
}

function Remove-SafeStagingDirectory {
    param(
        [string]$Path,
        [string]$AllowedBase
    )

    $directorySeparator = [System.IO.Path]::DirectorySeparatorChar
    $resolvedBase = [System.IO.Path]::GetFullPath($AllowedBase).TrimEnd($directorySeparator)
    $resolvedTarget = [System.IO.Path]::GetFullPath($Path).TrimEnd($directorySeparator)
    $requiredPrefix = $resolvedBase + $directorySeparator

    if (-not $resolvedTarget.StartsWith(
            $requiredPrefix,
            [System.StringComparison]::OrdinalIgnoreCase
        )) {
        throw "Refusing to remove a staging path outside the allowed base: $resolvedTarget"
    }

    if (Test-Path -LiteralPath $resolvedTarget) {
        Remove-Item -LiteralPath $resolvedTarget -Recurse -Force
    }
}

function Copy-MatchingArtifacts {
    param(
        [string]$SourceDirectory,
        [string]$DestinationDirectory,
        [string[]]$Patterns
    )

    $null = New-Item -ItemType Directory -Path $DestinationDirectory -Force

    foreach ($pattern in $Patterns) {
        Get-ChildItem -Path (Join-Path $SourceDirectory $pattern) -File -ErrorAction SilentlyContinue |
            Copy-Item -Destination $DestinationDirectory -Force
    }
}

$firmwareRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $firmwareRoot ".."))
$stm32Source = Join-Path $firmwareRoot "stm32_uart_mvp"
$esp32Source = Join-Path $firmwareRoot "esp32_uart_bridge"

if (-not (Test-Path -LiteralPath $projectRoot -PathType Container)) {
    throw "Project root was not found: $projectRoot"
}

$buildStm32 = $Target -in @("All", "STM32")
$buildEsp32 = $Target -in @("All", "ESP32")

if ($buildStm32 -and -not (Test-Path -LiteralPath (Join-Path $stm32Source ".project") -PathType Leaf)) {
    throw "STM32CubeIDE project was not found: $stm32Source"
}

if ($buildEsp32 -and -not (Test-Path -LiteralPath (Join-Path $esp32Source "CMakeLists.txt") -PathType Leaf)) {
    throw "ESP-IDF project was not found: $esp32Source"
}

if (-not (Get-Command robocopy.exe -ErrorAction SilentlyContinue)) {
    throw "robocopy.exe is required for isolated source copies."
}

$gitCommit = $null
$gitDirty = $null
$gitStatusLines = @()
$gitRoot = $null
$gitCommand = Get-Command git.exe -ErrorAction SilentlyContinue

if ($gitCommand) {
    $gitRootOutput = & $gitCommand.Source -C $projectRoot rev-parse --show-toplevel 2>$null
    $gitRootExitCode = $LASTEXITCODE

    if ($gitRootExitCode -eq 0) {
        $gitRoot = [System.IO.Path]::GetFullPath(($gitRootOutput | Select-Object -First 1).Trim())
        $projectPathSpec = [System.IO.Path]::GetRelativePath($gitRoot, $projectRoot).Replace("\", "/")

        $gitCommitOutput = & $gitCommand.Source -C $gitRoot rev-parse HEAD 2>$null
        if ($LASTEXITCODE -eq 0) {
            $gitCommit = ($gitCommitOutput | Select-Object -First 1).Trim()
        }

        $gitStatusLines = @(
            & $gitCommand.Source -C $gitRoot status --porcelain --untracked-files=all -- $projectPathSpec
        )
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to read Git status for $projectPathSpec"
        }

        $gitDirty = $gitStatusLines.Count -gt 0
    }
}

if ($RequireClean) {
    if (-not $gitCommand -or $null -eq $gitDirty) {
        throw "-RequireClean was requested, but Git status could not be determined."
    }

    if ($gitDirty) {
        throw "-RequireClean was requested, but the Tracked_Mobile_Robot project has uncommitted changes."
    }
}
elseif ($gitDirty) {
    Write-Warning "Building an uncommitted working tree. The manifest will record the dirty state."
}

$cubeCandidates = @(
    "C:\ST\STM32CubeIDE_2.1.1\STM32CubeIDE\headless-build.bat"
    $(
        Get-ChildItem -Path "C:\ST\STM32CubeIDE_*\STM32CubeIDE\headless-build.bat" -File -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            ForEach-Object FullName
    )
    $(
        if ($env:ProgramFiles) {
            Get-ChildItem -Path (Join-Path $env:ProgramFiles "STMicroelectronics\STM32CubeIDE*\STM32CubeIDE\headless-build.bat") -File -ErrorAction SilentlyContinue |
                Sort-Object LastWriteTime -Descending |
                ForEach-Object FullName
        }
    )
)

$profileCandidates = @(
    "C:\Espressif\tools\Microsoft.v6.0.2.PowerShell_profile.ps1"
    $(
        Get-ChildItem -Path "C:\Espressif\tools\Microsoft.*.PowerShell_profile.ps1" -File -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            ForEach-Object FullName
    )
)

$resolvedCubePath = $null
$resolvedEspProfilePath = $null

if ($buildStm32) {
    $cubeResolveParameters = @{
        RequestedPath = $CubeIdeHeadlessPath
        Candidates    = $cubeCandidates
        Description   = "STM32CubeIDE headless builder"
    }
    $resolvedCubePath = Resolve-ExistingFile @cubeResolveParameters
}

if ($buildEsp32) {
    $profileResolveParameters = @{
        RequestedPath = $EspIdfProfilePath
        Candidates    = $profileCandidates
        Description   = "ESP-IDF PowerShell profile"
    }
    $resolvedEspProfilePath = Resolve-ExistingFile @profileResolveParameters
}

if ([string]::IsNullOrWhiteSpace($ArtifactRoot)) {
    if ([string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)) {
        throw "LOCALAPPDATA is not defined. Pass -ArtifactRoot explicitly."
    }

    $ArtifactRoot = Join-Path $env:LOCALAPPDATA "TrackedMobileRobot\builds"
}

$resolvedArtifactBase = [System.IO.Path]::GetFullPath($ArtifactRoot)
$forbiddenArtifactRoot = if ($gitRoot) { $gitRoot } else { $projectRoot }
$forbiddenArtifactRoot = $forbiddenArtifactRoot.TrimEnd([System.IO.Path]::DirectorySeparatorChar)
$forbiddenArtifactPrefix = $forbiddenArtifactRoot +
    [System.IO.Path]::DirectorySeparatorChar

if (
    $resolvedArtifactBase.Equals($forbiddenArtifactRoot, [System.StringComparison]::OrdinalIgnoreCase) -or
    $resolvedArtifactBase.StartsWith($forbiddenArtifactPrefix, [System.StringComparison]::OrdinalIgnoreCase)
) {
    throw "ArtifactRoot must be outside the Git repository: $resolvedArtifactBase"
}

if ([string]::IsNullOrWhiteSpace($env:TEMP)) {
    throw "TEMP is not defined."
}

$runId = "{0}-{1}-{2}" -f (
    Get-Date -Format "yyyyMMddHHmmss"
), $PID, ([System.Guid]::NewGuid().ToString("N").Substring(0, 4))

$stageBase = [System.IO.Path]::GetFullPath((Join-Path $env:TEMP "tmr-fw"))
if (
    $stageBase.Equals($forbiddenArtifactRoot, [System.StringComparison]::OrdinalIgnoreCase) -or
    $stageBase.StartsWith($forbiddenArtifactPrefix, [System.StringComparison]::OrdinalIgnoreCase)
) {
    throw "TEMP resolves inside the Git repository. Pass a safe external TEMP location before building: $stageBase"
}

$stageRoot = Join-Path $stageBase $runId
$runArtifactRoot = Join-Path $resolvedArtifactBase $runId
$logRoot = Join-Path $runArtifactRoot "logs"
$outputRoot = Join-Path $runArtifactRoot "output"

$null = New-Item -ItemType Directory -Path $stageRoot -Force
$null = New-Item -ItemType Directory -Path $logRoot -Force
$null = New-Item -ItemType Directory -Path $outputRoot -Force

$startedAt = Get-Date
$buildSucceeded = $false
$stm32Manifest = $null
$esp32Manifest = $null

Write-Host "Project source : $projectRoot"
Write-Host "Staging root  : $stageRoot"
Write-Host "Artifact root : $runArtifactRoot"

try {
    if ($buildStm32) {
        $stm32Stage = Join-Path $stageRoot "stm"
        $stm32Workspace = Join-Path $stageRoot "ws"
        $stm32CopyLog = Join-Path $logRoot "stm32-copy.log"
        $stm32BuildLog = Join-Path $logRoot "stm32-build.log"

        $stm32CopyParameters = @{
            Source              = $stm32Source
            Destination         = $stm32Stage
            ExcludedDirectories = @("Debug", "Release", ".git")
            LogPath             = $stm32CopyLog
        }
        Copy-IsolatedTree @stm32CopyParameters

        $null = New-Item -ItemType Directory -Path $stm32Workspace -Force

        $stm32BuildParameters = @{
            FilePath    = $resolvedCubePath
            ArgumentList = @(
                "-data", $stm32Workspace,
                "-import", $stm32Stage,
                "-cleanBuild", "stm32_uart_mvp/$Configuration",
                "-no-indexer",
                "-markerType", "all",
                "-printErrorMarkers"
            )
            LogPath     = $stm32BuildLog
            Description = "STM32 $Configuration isolated build"
        }
        Invoke-LoggedNativeCommand @stm32BuildParameters

        $stm32BuildDirectory = Join-Path $stm32Stage $Configuration
        $stm32ElfPath = Join-Path $stm32BuildDirectory "stm32_uart_mvp.elf"
        if (-not (Test-Path -LiteralPath $stm32ElfPath -PathType Leaf)) {
            throw "STM32 build returned success but the ELF was not found: $stm32ElfPath"
        }

        $stm32OutputDirectory = Join-Path $outputRoot "stm32"
        $stm32ArtifactParameters = @{
            SourceDirectory      = $stm32BuildDirectory
            DestinationDirectory = $stm32OutputDirectory
            Patterns             = @("*.elf", "*.map", "*.list", "*.bin", "*.hex")
        }
        Copy-MatchingArtifacts @stm32ArtifactParameters

        $stm32Manifest = [ordered]@{
            configuration = $Configuration
            tool          = $resolvedCubePath
            output        = $stm32OutputDirectory
            log           = $stm32BuildLog
        }
    }

    if ($buildEsp32) {
        $esp32Stage = Join-Path $stageRoot "esp"
        $esp32BuildDirectory = Join-Path $esp32Stage "b"
        $esp32CopyLog = Join-Path $logRoot "esp32-copy.log"
        $esp32EnvironmentLog = Join-Path $logRoot "esp32-environment.log"
        $esp32BuildLog = Join-Path $logRoot "esp32-build.log"

        $esp32CopyParameters = @{
            Source              = $esp32Source
            Destination         = $esp32Stage
            ExcludedDirectories = @("build", "build-isolated", ".git")
            LogPath             = $esp32CopyLog
        }
        Copy-IsolatedTree @esp32CopyParameters

        # This installer-generated profile sets IDF_PATH, IDF_TOOLS_PATH,
        # IDF_PYTHON_ENV_PATH and the exact toolchain PATH for ESP-IDF v6.
        . $resolvedEspProfilePath

        $pythonCandidates = @(
            $(if ($env:IDF_PYTHON_ENV_PATH) { Join-Path $env:IDF_PYTHON_ENV_PATH "Scripts\python.exe" })
            "C:\Espressif\tools\python\v6.0.2\venv\Scripts\python.exe"
        )
        $idfPyCandidates = @(
            $(if ($env:IDF_PATH) { Join-Path $env:IDF_PATH "tools\idf.py" })
            "C:\esp\v6.0.2\esp-idf\tools\idf.py"
        )

        $pythonResolveParameters = @{
            RequestedPath = $EspPythonPath
            Candidates    = $pythonCandidates
            Description   = "ESP-IDF Python interpreter"
        }
        $resolvedEspPythonPath = Resolve-ExistingFile @pythonResolveParameters

        $idfPyResolveParameters = @{
            RequestedPath = $IdfPyPath
            Candidates    = $idfPyCandidates
            Description   = "ESP-IDF idf.py"
        }
        $resolvedIdfPyPath = Resolve-ExistingFile @idfPyResolveParameters

        @(
            "profile=$resolvedEspProfilePath"
            "python=$resolvedEspPythonPath"
            "idf_py=$resolvedIdfPyPath"
            "IDF_PATH=$($env:IDF_PATH)"
            "IDF_TOOLS_PATH=$($env:IDF_TOOLS_PATH)"
            "IDF_PYTHON_ENV_PATH=$($env:IDF_PYTHON_ENV_PATH)"
        ) | Set-Content -LiteralPath $esp32EnvironmentLog -Encoding utf8

        $esp32BuildParameters = @{
            FilePath     = $resolvedEspPythonPath
            ArgumentList = @(
                $resolvedIdfPyPath,
                "-C", $esp32Stage,
                "-B", $esp32BuildDirectory,
                "build"
            )
            LogPath      = $esp32BuildLog
            Description  = "ESP32-S3 isolated build"
        }
        Invoke-LoggedNativeCommand @esp32BuildParameters

        $esp32AppBinary = Join-Path $esp32BuildDirectory "esp32_uart_bridge.bin"
        if (-not (Test-Path -LiteralPath $esp32AppBinary -PathType Leaf)) {
            throw "ESP32 build returned success but the application binary was not found: $esp32AppBinary"
        }

        $esp32OutputDirectory = Join-Path $outputRoot "esp32"
        $esp32ArtifactParameters = @{
            SourceDirectory      = $esp32BuildDirectory
            DestinationDirectory = $esp32OutputDirectory
            Patterns             = @(
                "esp32_uart_bridge.bin",
                "esp32_uart_bridge.elf",
                "esp32_uart_bridge.map",
                "flash_args",
                "flasher_args.json"
            )
        }
        Copy-MatchingArtifacts @esp32ArtifactParameters

        $bootloaderBinary = Join-Path $esp32BuildDirectory "bootloader\bootloader.bin"
        if (Test-Path -LiteralPath $bootloaderBinary -PathType Leaf) {
            Copy-Item -LiteralPath $bootloaderBinary -Destination (Join-Path $esp32OutputDirectory "bootloader.bin") -Force
        }

        $partitionTableBinary = Join-Path $esp32BuildDirectory "partition_table\partition-table.bin"
        if (Test-Path -LiteralPath $partitionTableBinary -PathType Leaf) {
            Copy-Item -LiteralPath $partitionTableBinary -Destination (Join-Path $esp32OutputDirectory "partition-table.bin") -Force
        }

        $esp32Manifest = [ordered]@{
            profile = $resolvedEspProfilePath
            python  = $resolvedEspPythonPath
            idf_py  = $resolvedIdfPyPath
            target  = "esp32s3"
            output  = $esp32OutputDirectory
            log     = $esp32BuildLog
        }
    }

    $manifest = [ordered]@{
        run_id       = $runId
        started_at   = $startedAt.ToString("o")
        completed_at = (Get-Date).ToString("o")
        source_root  = $projectRoot
        git_commit   = $gitCommit
        git_dirty    = $gitDirty
        git_status   = $gitStatusLines
        target       = $Target
        stm32        = $stm32Manifest
        esp32        = $esp32Manifest
    }

    $manifest | ConvertTo-Json -Depth 6 |
        Set-Content -LiteralPath (Join-Path $runArtifactRoot "manifest.json") -Encoding utf8

    $buildSucceeded = $true
    Write-Host "`nBuild completed successfully."
    Write-Host "Artifacts: $runArtifactRoot"
}
catch {
    $failureMessage = $_.Exception.Message
    @(
        "failed_at=$((Get-Date).ToString('o'))"
        "message=$failureMessage"
        "stage=$stageRoot"
    ) | Set-Content -LiteralPath (Join-Path $runArtifactRoot "failure.txt") -Encoding utf8

    Write-Error "$failureMessage`nStaging was preserved at: $stageRoot`nLogs: $logRoot" -ErrorAction Continue
    throw
}
finally {
    if ($buildSucceeded -and -not $KeepStage) {
        try {
            Remove-SafeStagingDirectory -Path $stageRoot -AllowedBase $stageBase
            Write-Host "Removed verified staging directory: $stageRoot"
        }
        catch {
            Write-Warning "Build succeeded, but staging cleanup was refused or failed: $($_.Exception.Message)"
        }
    }
    elseif (Test-Path -LiteralPath $stageRoot) {
        Write-Host "Staging preserved at: $stageRoot"
    }
}
