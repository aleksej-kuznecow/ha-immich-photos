# Immich Photos

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

This custom integration for Home Assistant provides a `camera` entity with photo frame from Immich (self-hosted photo and video management solution).

**This integration will set up the following platforms.**

Platform | Description
-- | --
`camera` | A random image from the random Immich Album.

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `immich_photos`.
1. Download _all_ the files from the `custom_components/immich_photos/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant

## Configuration
1. Add the part of configuration provided below to your `configuration.yaml`
1. Replace `any.valid.url.with.immich.api.available` in the added text with the valid URL of your Immich.
1. Replace `ani.valid.api.key.provided.by.immich` in the added text with the valid API key peovided by your Immich (get or add it here in your Immich: Accountsettings/API Keys).
1. Again restart Home Assistant

### configuration.yaml required part 
~~~
camera:
  - platform: immich_photos
    url: "http://any.valid.url.with.immich.api.available"
    api_key: "ani.valid.api.key.provided.by.immich"
~~~

## Examples
### Dashboard Picture card
~~~
type: picture-entity
entity: camera.album_image
show_state: false
show_name: false
camera_view: auto
aspect_ratio: '16:9'
~~~

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[integration_blueprint]: https://github.com/aleksej-kuznecow/ha-immich-photos
[buymecoffee]: https://www.buymeacoffee.com/aleksej.kuznecow
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/aleksej-kuznecow/ha-immich-photos.svg?style=for-the-badge
[commits]: https://github.com/aleksej-kuznecow/ha-immich-photos/commits/main
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/aleksej-kuznecow/ha-immich-photos.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Aleksej%20Kuznetsov%20%40aleksej--kuznecow-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/aleksej-kuznecow/ha-immich-photos.svg?style=for-the-badge
[releases]: https://github.com/aleksej-kuznecow/ha-immich-photos/releases
