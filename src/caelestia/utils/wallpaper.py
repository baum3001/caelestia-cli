import random
from argparse import Namespace
from pathlib import Path

from materialyoucolor.hct import Hct
from materialyoucolor.utils.color_utils import argb_from_rgb
from PIL import Image

from caelestia.utils.hypr import message
from caelestia.utils.material import get_colours_for_image
from caelestia.utils.paths import (
    compute_hash,
    wallpaper_link_path,
    wallpaper_path_path,
    wallpaper_thumbnail_path,
    wallpapers_cache_dir,
)
from caelestia.utils.scheme import Scheme, get_scheme
from caelestia.utils.theme import apply_colours


def is_valid_image(path: Path | str) -> bool:
    path = Path(path)
    return path.is_file() and path.suffix in [".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"]


def check_wall(wall: Path, filter_size: tuple[int, int], threshold: float) -> bool:
    with Image.open(wall) as img:
        width, height = img.size
        return width >= filter_size[0] * threshold and height >= filter_size[1] * threshold


def get_wallpaper() -> str:
    try:
        return wallpaper_path_path.read_text()
    except IOError:
        return None


def get_wallpapers(args: Namespace) -> list[Path]:
    dir = Path(args.random)
    if not dir.is_dir():
        return []

    walls = [f for f in dir.rglob("*") if is_valid_image(f)]

    if args.no_filter:
        return walls

    monitors = message("monitors")
    filter_size = monitors[0]["width"], monitors[0]["height"]
    for monitor in monitors[1:]:
        if filter_size[0] > monitor["width"]:
            filter_size[0] = monitor["width"]
        if filter_size[1] > monitor["height"]:
            filter_size[1] = monitor["height"]

    return [f for f in walls if check_wall(f, filter_size, args.threshold)]


def get_thumb(wall: Path, cache: Path) -> Path:
    thumb = cache / "thumbnail.jpg"

    if not thumb.exists():
        with Image.open(wall) as img:
            img = img.convert("RGB")
            img.thumbnail((128, 128), Image.NEAREST)
            thumb.parent.mkdir(parents=True, exist_ok=True)
            img.save(thumb, "JPEG")

    return thumb


def get_smart_mode(wall: Path, cache: Path) -> str:
    mode_cache = cache / "mode.txt"

    try:
        return mode_cache.read_text()
    except IOError:
        with Image.open(get_thumb(wall, cache)) as img:
            img.thumbnail((1, 1), Image.LANCZOS)
            mode = "light" if Hct.from_int(argb_from_rgb(*img.getpixel((0, 0)))).tone > 60 else "dark"

        mode_cache.parent.mkdir(parents=True, exist_ok=True)
        mode_cache.write_text(mode)

        return mode


def get_colours_for_wall(wall: Path | str, no_smart: bool) -> None:
    scheme = get_scheme()
    cache = wallpapers_cache_dir / compute_hash(wall)

    name = "dynamic"
    flavour = scheme.flavour if scheme.flavour in ("default", "alt1", "alt2") else "default"

    if not no_smart:
        scheme = Scheme(
            {
                "name": name,
                "flavour": flavour,
                "mode": get_smart_mode(wall, cache),
                "variant": scheme.variant,
                "colours": scheme.colours,
            }
        )

    return {
        "name": name,
        "flavour": flavour,
        "mode": scheme.mode,
        "variant": scheme.variant,
        "colours": get_colours_for_image(get_thumb(wall, cache), scheme),
    }


def set_wallpaper(wall: Path | str, no_smart: bool) -> None:
    if not is_valid_image(wall):
        raise ValueError(f'"{wall}" is not a valid image')

    # Update files
    wallpaper_path_path.parent.mkdir(parents=True, exist_ok=True)
    wallpaper_path_path.write_text(str(wall))
    wallpaper_link_path.parent.mkdir(parents=True, exist_ok=True)
    wallpaper_link_path.unlink(missing_ok=True)
    wallpaper_link_path.symlink_to(wall)

    cache = wallpapers_cache_dir / compute_hash(wall)

    # Generate thumbnail or get from cache
    thumb = get_thumb(wall, cache)
    wallpaper_thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
    wallpaper_thumbnail_path.unlink(missing_ok=True)
    wallpaper_thumbnail_path.symlink_to(thumb)

    scheme = get_scheme()

    # Change mode based on wallpaper colour
    if scheme.name == "dynamic" and not no_smart:
        scheme.mode = get_smart_mode(wall, cache)

    # Update colours
    scheme.update_colours()
    #apply_colours(scheme.colours, scheme.mode) breaks on nixos, also not needed in nixos


def set_random(args: Namespace) -> None:
    set_wallpaper(random.choice(get_wallpapers(args)), args.no_smart)
