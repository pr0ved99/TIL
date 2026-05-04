#!/usr/bin/env python3
"""Filter small occupied-cell noise from a Nav2 map YAML/PGM pair."""

import argparse
from collections import deque
from pathlib import Path

import yaml


FREE_VALUE = 254
UNKNOWN_VALUE = 205


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("map_yaml", help="Input Nav2 map YAML file.")
    parser.add_argument(
        "--output-prefix",
        help="Output prefix. Writes <prefix>.yaml and <prefix>.pgm.",
    )
    parser.add_argument(
        "--occupied-threshold",
        type=int,
        default=100,
        help="PGM values <= this are treated as occupied. Default: 100.",
    )
    parser.add_argument(
        "--min-obstacle-pixels",
        type=int,
        default=12,
        help="Remove occupied connected components smaller than this pixel count.",
    )
    parser.add_argument(
        "--min-occupied-neighbors",
        type=int,
        default=1,
        help=(
            "Remove occupied pixels that have fewer occupied neighbors in the "
            "8-neighborhood before connected-component filtering."
        ),
    )
    parser.add_argument(
        "--replace-with",
        choices=("free", "unknown"),
        default="free",
        help="Value used when removing noise cells. Default: free.",
    )
    return parser.parse_args()


def read_map_yaml(path):
    with Path(path).open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    if not isinstance(data, dict) or "image" not in data:
        raise ValueError(f"{path} is not a valid Nav2 map YAML file")
    return data


def resolve_image_path(map_yaml_path, image_value):
    image_path = Path(image_value)
    if not image_path.is_absolute():
        image_path = Path(map_yaml_path).parent / image_path
    return image_path


def _next_pgm_token(raw, index):
    size = len(raw)
    while index < size:
        byte = raw[index]
        if byte == ord("#"):
            while index < size and raw[index] not in (ord("\n"), ord("\r")):
                index += 1
        elif chr(byte).isspace():
            index += 1
        else:
            break
    start = index
    while index < size and not chr(raw[index]).isspace():
        index += 1
    return raw[start:index].decode("ascii"), index


def read_pgm(path):
    raw = Path(path).read_bytes()
    magic, index = _next_pgm_token(raw, 0)
    width_token, index = _next_pgm_token(raw, index)
    height_token, index = _next_pgm_token(raw, index)
    max_value_token, index = _next_pgm_token(raw, index)

    width = int(width_token)
    height = int(height_token)
    max_value = int(max_value_token)
    if max_value > 255:
        raise ValueError("Only 8-bit PGM files are supported")

    if magic == "P5":
        while index < len(raw) and chr(raw[index]).isspace():
            index += 1
        pixels = bytearray(raw[index : index + width * height])
    elif magic == "P2":
        pixels = bytearray()
        for _ in range(width * height):
            token, index = _next_pgm_token(raw, index)
            pixels.append(int(token))
    else:
        raise ValueError(f"Unsupported PGM magic: {magic}")

    if len(pixels) != width * height:
        raise ValueError(
            f"PGM pixel count mismatch: expected {width * height}, got {len(pixels)}"
        )
    return width, height, max_value, pixels


def write_pgm(path, width, height, max_value, pixels):
    header = f"P5\n# Filtered by Tools/filter_nav2_saved_map.py\n{width} {height}\n{max_value}\n"
    Path(path).write_bytes(header.encode("ascii") + bytes(pixels))


def is_occupied(value, occupied_threshold):
    return value <= occupied_threshold


def neighbor_offsets(width, height, index):
    row, col = divmod(index, width)
    for drow in (-1, 0, 1):
        for dcol in (-1, 0, 1):
            if drow == 0 and dcol == 0:
                continue
            next_row = row + drow
            next_col = col + dcol
            if 0 <= next_row < height and 0 <= next_col < width:
                yield next_row * width + next_col


def remove_sparse_occupied_pixels(pixels, width, height, occupied_threshold, min_neighbors):
    if min_neighbors <= 0:
        return 0

    to_remove = []
    for index, value in enumerate(pixels):
        if not is_occupied(value, occupied_threshold):
            continue
        neighbors = sum(
            1
            for neighbor in neighbor_offsets(width, height, index)
            if is_occupied(pixels[neighbor], occupied_threshold)
        )
        if neighbors < min_neighbors:
            to_remove.append(index)

    for index in to_remove:
        pixels[index] = FREE_VALUE
    return len(to_remove)


def remove_small_components(
    pixels,
    width,
    height,
    occupied_threshold,
    min_obstacle_pixels,
    replacement_value,
):
    visited = bytearray(len(pixels))
    removed_components = 0
    removed_pixels = 0
    kept_components = 0

    for start_index, value in enumerate(pixels):
        if visited[start_index] or not is_occupied(value, occupied_threshold):
            continue

        component = []
        queue = deque([start_index])
        visited[start_index] = 1

        while queue:
            index = queue.popleft()
            component.append(index)
            for neighbor in neighbor_offsets(width, height, index):
                if visited[neighbor] or not is_occupied(pixels[neighbor], occupied_threshold):
                    continue
                visited[neighbor] = 1
                queue.append(neighbor)

        if len(component) < min_obstacle_pixels:
            removed_components += 1
            removed_pixels += len(component)
            for index in component:
                pixels[index] = replacement_value
        else:
            kept_components += 1

    return removed_components, removed_pixels, kept_components


def count_occupied(pixels, occupied_threshold):
    return sum(1 for value in pixels if is_occupied(value, occupied_threshold))


def main():
    args = parse_args()
    map_yaml_path = Path(args.map_yaml)
    map_data = read_map_yaml(map_yaml_path)
    image_path = resolve_image_path(map_yaml_path, map_data["image"])

    width, height, max_value, pixels = read_pgm(image_path)
    before_occupied = count_occupied(pixels, args.occupied_threshold)
    sparse_removed = remove_sparse_occupied_pixels(
        pixels,
        width,
        height,
        args.occupied_threshold,
        args.min_occupied_neighbors,
    )
    replacement_value = FREE_VALUE if args.replace_with == "free" else UNKNOWN_VALUE
    removed_components, removed_pixels, kept_components = remove_small_components(
        pixels,
        width,
        height,
        args.occupied_threshold,
        args.min_obstacle_pixels,
        replacement_value,
    )
    after_occupied = count_occupied(pixels, args.occupied_threshold)

    if args.output_prefix:
        output_prefix = Path(args.output_prefix)
    else:
        input_prefix = map_yaml_path.with_suffix("")
        output_prefix = input_prefix.parent / f"{input_prefix.name}_filtered"
    output_yaml_path = output_prefix.with_suffix(".yaml")
    output_pgm_path = output_prefix.with_suffix(".pgm")
    output_yaml_path.parent.mkdir(parents=True, exist_ok=True)

    write_pgm(output_pgm_path, width, height, max_value, pixels)
    output_data = dict(map_data)
    output_data["image"] = output_pgm_path.name
    with output_yaml_path.open("w", encoding="utf-8") as stream:
        yaml.safe_dump(output_data, stream, sort_keys=False)

    print(f"Input map: {map_yaml_path}")
    print(f"Input image: {image_path}")
    print(f"Output map: {output_yaml_path}")
    print(f"Output image: {output_pgm_path}")
    print(f"Map size: {width}x{height}")
    print(f"Occupied before: {before_occupied}")
    print(f"Sparse occupied pixels removed: {sparse_removed}")
    print(f"Small occupied components removed: {removed_components}")
    print(f"Small occupied component pixels removed: {removed_pixels}")
    print(f"Kept occupied components: {kept_components}")
    print(f"Occupied after: {after_occupied}")


if __name__ == "__main__":
    main()
