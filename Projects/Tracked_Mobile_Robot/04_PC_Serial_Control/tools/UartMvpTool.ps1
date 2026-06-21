param(
    [ValidateSet("ListPorts", "Build", "Send", "Monitor", "Interactive", "ScriptedTest")]
    [string]$Mode = "Interactive",

    [string]$Port = "",
    [int]$Baudrate = 115200,

    [ValidateSet("PING", "ARM", "DISARM", "CMD", "RAW")]
    [string]$Frame = "PING",

    [int]$Seq = 1,
    [int]$VxMmps = 0,
    [int]$WMradps = 0,
    [int]$TimeoutMs = 300,
    [string]$Raw = "",

    [double]$WaitS = 1.0,
    [string]$LogDir = "logs",
    [switch]$DryRun,
    [switch]$NoLog
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$script:RawLogPath = $null
$script:CsvLogPath = $null
$script:LoggingEnabled = -not $NoLog

function New-UartFrame {
    param(
        [string]$Type,
        [int]$Seq,
        [int]$VxMmps,
        [int]$WMradps,
        [int]$TimeoutMs,
        [string]$Raw
    )

    switch ($Type.ToUpperInvariant()) {
        "PING" { return "PING,seq=$Seq`n" }
        "ARM" { return "ARM,seq=$Seq`n" }
        "DISARM" { return "DISARM,seq=$Seq`n" }
        "CMD" {
            if ($VxMmps -lt -100 -or $VxMmps -gt 100) {
                throw "vx_mmps out of MVP range: $VxMmps"
            }
            if ($WMradps -lt -500 -or $WMradps -gt 500) {
                throw "w_mradps out of MVP range: $WMradps"
            }
            if ($TimeoutMs -lt 50 -or $TimeoutMs -gt 500) {
                throw "timeout_ms out of MVP range: $TimeoutMs"
            }
            return "CMD,seq=$Seq,vx_mmps=$VxMmps,w_mradps=$WMradps,timeout_ms=$TimeoutMs`n"
        }
        "RAW" {
            if ($Raw.EndsWith("`n")) {
                return $Raw
            }
            return "$Raw`n"
        }
        default {
            throw "Unsupported frame type: $Type"
        }
    }
}

function Get-ParsedFrame {
    param([string]$Line)

    $rawLine = $Line.TrimEnd("`r", "`n")
    $result = @{
        Type = ""
        Seq = ""
        State = ""
        Code = ""
        Category = "unparsed"
        Raw = $rawLine
    }

    if ([string]::IsNullOrWhiteSpace($rawLine)) {
        return $result
    }

    $tokens = $rawLine.Split(",")
    $result.Type = $tokens[0].Trim().ToUpperInvariant()
    for ($i = 1; $i -lt $tokens.Length; $i++) {
        $token = $tokens[$i]
        $eq = $token.IndexOf("=")
        if ($eq -lt 0) {
            continue
        }
        $key = $token.Substring(0, $eq).Trim()
        $value = $token.Substring($eq + 1).Trim()
        switch ($key) {
            "seq" { $result.Seq = $value }
            "state" { $result.State = $value }
            "code" { $result.Code = $value }
        }
    }

    switch ($result.Type) {
        "ACK" { $result.Category = "accepted" }
        "ERR" { $result.Category = "rejected" }
        "TEL" { $result.Category = "telemetry" }
        "PONG" { $result.Category = "pong" }
        "STATE" { $result.Category = "state" }
        "FAULT" { $result.Category = "fault" }
        default { $result.Category = "other" }
    }

    return $result
}

function Escape-Csv {
    param([string]$Text)
    if ($null -eq $Text) {
        return ""
    }
    $escaped = $Text.Replace('"', '""')
    return '"' + $escaped + '"'
}

function Initialize-UartLog {
    if (-not $script:LoggingEnabled) {
        return
    }

    New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $script:RawLogPath = Join-Path $LogDir "uart_mvp_${stamp}_raw.log"
    $script:CsvLogPath = Join-Path $LogDir "uart_mvp_${stamp}_parsed.csv"

    "timestamp,direction,frame_type,seq,state,code,category,raw" |
        Set-Content -Path $script:CsvLogPath -Encoding UTF8
}

function Write-UartLog {
    param(
        [string]$Direction,
        [string]$Line
    )

    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffK"
    $stripped = $Line.TrimEnd("`r", "`n")
    Write-Host ("{0} {1,-2} {2}" -f $timestamp, $Direction, $stripped)

    if (-not $script:LoggingEnabled) {
        return
    }

    Add-Content -Path $script:RawLogPath -Encoding UTF8 -Value "$timestamp $Direction $stripped"

    $parsed = Get-ParsedFrame -Line $stripped
    $csvLine = @(
        Escape-Csv $timestamp
        Escape-Csv $Direction
        Escape-Csv $parsed.Type
        Escape-Csv $parsed.Seq
        Escape-Csv $parsed.State
        Escape-Csv $parsed.Code
        Escape-Csv $parsed.Category
        Escape-Csv $parsed.Raw
    ) -join ","
    Add-Content -Path $script:CsvLogPath -Encoding UTF8 -Value $csvLine
}

function Open-UartPort {
    param(
        [string]$Port,
        [int]$Baudrate
    )

    $serial = [System.IO.Ports.SerialPort]::new(
        $Port,
        $Baudrate,
        [System.IO.Ports.Parity]::None,
        8,
        [System.IO.Ports.StopBits]::One
    )
    $serial.NewLine = "`n"
    $serial.ReadTimeout = 100
    $serial.WriteTimeout = 500
    $serial.Open()
    return $serial
}

function Send-UartFrame {
    param(
        [System.IO.Ports.SerialPort]$Serial,
        [string]$FrameText
    )

    $Serial.Write($FrameText)
    Write-UartLog -Direction "TX" -Line $FrameText
}

function Read-UartFor {
    param(
        [System.IO.Ports.SerialPort]$Serial,
        [double]$Seconds
    )

    $deadline = (Get-Date).AddMilliseconds([int]($Seconds * 1000.0))
    while ((Get-Date) -lt $deadline) {
        try {
            $line = $Serial.ReadLine()
            Write-UartLog -Direction "RX" -Line $line
        }
        catch [System.TimeoutException] {
        }
    }
}

function Require-Port {
    if ([string]::IsNullOrWhiteSpace($Port)) {
        throw "Port is required. Example: -Port COM5"
    }
}

function Invoke-ListPorts {
    $ports = @([System.IO.Ports.SerialPort]::GetPortNames() | Sort-Object)
    if ($ports.Count -eq 0) {
        Write-Host "No serial ports found."
        return
    }
    foreach ($p in $ports) {
        Write-Host $p
    }
}

function Invoke-Build {
    $frameText = New-UartFrame -Type $Frame -Seq $Seq -VxMmps $VxMmps -WMradps $WMradps -TimeoutMs $TimeoutMs -Raw $Raw
    Write-Host $frameText -NoNewline
}

function Invoke-Send {
    $frameText = New-UartFrame -Type $Frame -Seq $Seq -VxMmps $VxMmps -WMradps $WMradps -TimeoutMs $TimeoutMs -Raw $Raw
    if ($DryRun) {
        Write-Host $frameText -NoNewline
        return
    }

    Require-Port
    Initialize-UartLog
    $serial = Open-UartPort -Port $Port -Baudrate $Baudrate
    try {
        Send-UartFrame -Serial $serial -FrameText $frameText
        Read-UartFor -Serial $serial -Seconds $WaitS
    }
    finally {
        $serial.Close()
    }
}

function Invoke-Monitor {
    Require-Port
    Initialize-UartLog
    $serial = Open-UartPort -Port $Port -Baudrate $Baudrate
    try {
        Write-Host "Monitoring. Press Ctrl+C to stop."
        while ($true) {
            Read-UartFor -Serial $serial -Seconds 0.2
        }
    }
    finally {
        $serial.Close()
    }
}

function Get-ScriptedFrames {
    return @(
        @{ Frame = (New-UartFrame -Type "PING" -Seq 1 -VxMmps 0 -WMradps 0 -TimeoutMs 300 -Raw ""); Wait = 0.5 },
        @{ Frame = (New-UartFrame -Type "CMD" -Seq 2 -VxMmps 80 -WMradps 0 -TimeoutMs 300 -Raw ""); Wait = 0.5 },
        @{ Frame = (New-UartFrame -Type "ARM" -Seq 3 -VxMmps 0 -WMradps 0 -TimeoutMs 300 -Raw ""); Wait = 0.5 },
        @{ Frame = (New-UartFrame -Type "CMD" -Seq 4 -VxMmps 80 -WMradps 0 -TimeoutMs 300 -Raw ""); Wait = 0.5 },
        @{ Frame = (New-UartFrame -Type "RAW" -Seq 5 -VxMmps 0 -WMradps 0 -TimeoutMs 300 -Raw "CMD,seq=5,vx_mmps=80,timeout_ms=300"); Wait = 0.5 },
        @{ Frame = (New-UartFrame -Type "RAW" -Seq 6 -VxMmps 0 -WMradps 0 -TimeoutMs 300 -Raw "CMD,seq=6,vx_mmps=9999,w_mradps=0,timeout_ms=300"); Wait = 0.5 },
        @{ Frame = (New-UartFrame -Type "CMD" -Seq 7 -VxMmps 0 -WMradps 0 -TimeoutMs 300 -Raw ""); Wait = 1.0 },
        @{ Frame = (New-UartFrame -Type "DISARM" -Seq 8 -VxMmps 0 -WMradps 0 -TimeoutMs 300 -Raw ""); Wait = 0.5 }
    )
}

function Invoke-ScriptedTest {
    $items = Get-ScriptedFrames
    if ($DryRun) {
        foreach ($item in $items) {
            Write-Host $item.Frame -NoNewline
            Write-Host ("# wait {0}s" -f $item.Wait)
        }
        return
    }

    Require-Port
    Initialize-UartLog
    $serial = Open-UartPort -Port $Port -Baudrate $Baudrate
    try {
        foreach ($item in $items) {
            Send-UartFrame -Serial $serial -FrameText $item.Frame
            Read-UartFor -Serial $serial -Seconds $item.Wait
        }
    }
    finally {
        $serial.Close()
    }
}

function Read-IntWithDefault {
    param(
        [string]$Prompt,
        [int]$Default
    )
    $value = Read-Host "$Prompt [$Default]"
    if ([string]::IsNullOrWhiteSpace($value)) {
        return $Default
    }
    return [int]$value
}

function Invoke-Interactive {
    Require-Port
    Initialize-UartLog
    $serial = Open-UartPort -Port $Port -Baudrate $Baudrate
    $nextSeq = $Seq

    try {
        Write-Host "Interactive UART MVP console. Keep motor power disconnected."
        while ($true) {
            Write-Host ""
            Write-Host "1) PING"
            Write-Host "2) ARM"
            Write-Host "3) DISARM"
            Write-Host "4) CMD custom"
            Write-Host "5) CMD zero once"
            Write-Host "6) zero-CMD keepalive"
            Write-Host "7) raw frame"
            Write-Host "8) out-of-range CMD"
            Write-Host "9) monitor wait"
            Write-Host "q) quit"
            $choice = (Read-Host ">").Trim().ToLowerInvariant()

            if ($choice -eq "q") {
                break
            }

            $frameText = $null
            switch ($choice) {
                "1" {
                    $frameText = New-UartFrame -Type "PING" -Seq $nextSeq -VxMmps 0 -WMradps 0 -TimeoutMs 300 -Raw ""
                    $nextSeq++
                }
                "2" {
                    $frameText = New-UartFrame -Type "ARM" -Seq $nextSeq -VxMmps 0 -WMradps 0 -TimeoutMs 300 -Raw ""
                    $nextSeq++
                }
                "3" {
                    $frameText = New-UartFrame -Type "DISARM" -Seq $nextSeq -VxMmps 0 -WMradps 0 -TimeoutMs 300 -Raw ""
                    $nextSeq++
                }
                "4" {
                    $vx = Read-IntWithDefault -Prompt "vx_mmps" -Default 0
                    $w = Read-IntWithDefault -Prompt "w_mradps" -Default 0
                    $timeout = Read-IntWithDefault -Prompt "timeout_ms" -Default 300
                    $frameText = New-UartFrame -Type "CMD" -Seq $nextSeq -VxMmps $vx -WMradps $w -TimeoutMs $timeout -Raw ""
                    $nextSeq++
                }
                "5" {
                    $frameText = New-UartFrame -Type "CMD" -Seq $nextSeq -VxMmps 0 -WMradps 0 -TimeoutMs 300 -Raw ""
                    $nextSeq++
                }
                "6" {
                    $durationInput = Read-Host "duration_s [3.0]"
                    $durationS = 3.0
                    if (-not [string]::IsNullOrWhiteSpace($durationInput)) {
                        $durationS = [double]$durationInput
                    }
                    if ($durationS -le 0.0) {
                        $durationS = 3.0
                    }
                    $deadline = (Get-Date).AddMilliseconds([int]($durationS * 1000.0))
                    while ((Get-Date) -lt $deadline) {
                        $frameText = New-UartFrame -Type "CMD" -Seq $nextSeq -VxMmps 0 -WMradps 0 -TimeoutMs 300 -Raw ""
                        Send-UartFrame -Serial $serial -FrameText $frameText
                        Read-UartFor -Serial $serial -Seconds 0.02
                        $nextSeq++
                        Start-Sleep -Milliseconds 50
                    }
                    continue
                }
                "7" {
                    $rawFrame = Read-Host "raw frame without LF"
                    $frameText = New-UartFrame -Type "RAW" -Seq $nextSeq -VxMmps 0 -WMradps 0 -TimeoutMs 300 -Raw $rawFrame
                }
                "8" {
                    $frameText = New-UartFrame -Type "RAW" -Seq $nextSeq -VxMmps 0 -WMradps 0 -TimeoutMs 300 -Raw "CMD,seq=$nextSeq,vx_mmps=9999,w_mradps=0,timeout_ms=300"
                    $nextSeq++
                }
                "9" {
                    $waitInput = Read-Host "wait_s [2.0]"
                    $waitSeconds = 2.0
                    if (-not [string]::IsNullOrWhiteSpace($waitInput)) {
                        $waitSeconds = [double]$waitInput
                    }
                    Read-UartFor -Serial $serial -Seconds $waitSeconds
                    continue
                }
                default {
                    Write-Host "Unknown menu option."
                    continue
                }
            }

            Send-UartFrame -Serial $serial -FrameText $frameText
            Read-UartFor -Serial $serial -Seconds $WaitS
        }
    }
    finally {
        $serial.Close()
    }
}

switch ($Mode) {
    "ListPorts" { Invoke-ListPorts }
    "Build" { Invoke-Build }
    "Send" { Invoke-Send }
    "Monitor" { Invoke-Monitor }
    "Interactive" { Invoke-Interactive }
    "ScriptedTest" { Invoke-ScriptedTest }
}
