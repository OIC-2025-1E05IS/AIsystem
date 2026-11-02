[app]

title = KEIBA MONEY
package.name = keibamoney
package.domain = jp.oic2025
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,md
version = 1.0.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0

# No network permission is needed; race records remain on the device.
android.permissions =
android.api = 35
android.minapi = 23
android.archs = arm64-v8a
android.allow_backup = True

[buildozer]

log_level = 2
warn_on_root = 1
