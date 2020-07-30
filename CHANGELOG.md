# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security
### Translation Updates

## [0.2.6] - 2020-07-30

### Changed

- SGT Puzzles Collection has moved to GitHub and Transifex!
  - [Homepage](https://github.com/bluesabre/sgt-launcher)
  - [Releases](https://github.com/bluesabre/sgt-launcher/releases)
  - [Bug Reports](https://github.com/bluesabre/sgt-launcher/issues)
  - [Translations](https://www.transifex.com/bluesabreorg/sgt-puzzles-collection)
  - [Wiki](https://github.com/bluesabre/sgt-launcher/wiki)
- Updated README and URLs
- Migrated NEWS to CHANGELOG.md

### Fixed

- Syntax issues in SgtLauncher.py (#2)

### Translation Updates

Chinese (China), Danish, Lithuanian, Ukrainian

## [0.2.5] - 2020-02-19

### Added

- "Report a Bug..." option to the application menu
- Application shutdown with Ctrl-C in terminal
- Additional AppStream details

### Changed

- Move to RDN-format (sgt-launcher.desktop to org.bluesabre.SgtLauncher.desktop)
  for appdata and the launcher
  - Source installations may result in duplicate .desktop files, just delete 
    sgt-launcher.desktop)

### Fixed

- Game launching loop (LP: [#1697107](https://bugs.launchpad.net/bugs/1697107))
- AppStream validation

### Translation Updates

Danish

## [0.2.4] - 2018-04-11

### Translation Updates

Danish, Dutch, French, Lithuanian, Portuguese

## [0.2.3] - 2017-10-03

### Removed

- Unused "Preferences" menu item (LP: [#1686667](https://bugs.launchpad.net/bugs/1686667))

### Translation Updates

Kurdish, Polish, Spanish

## [0.2.2] - 2017-01-29

### Added

- [AppStream](https://www.freedesktop.org/wiki/Distributions/AppStream/) data

### Fixed

- Do not display non-existent launchers
- Link the launcher to the correct binary when packaged

## [0.2.1] - 2016-12-08

### Fixed

- Typo in sgt-launcher.desktop

## [0.2.0] - 2016-12-08

### Added

- Install to PREFIX/games
- Add keywords to desktop file

### Changed

- Improved manpage
- Upgraded license to GPL-3 or newer

## [0.1.0] - 2016-11-03

### Added

- Initial release

[unreleased]: https://github.com/bluesabre/sgt-launcher/compare/sgt-launcher-0.2.6...HEAD
[0.2.6]: https://github.com/bluesabre/sgt-launcher/compare/sgt-launcher-0.2.5...sgt-launcher-0.2.6
[0.2.5]: https://github.com/bluesabre/sgt-launcher/compare/sgt-launcher-0.2.4...sgt-launcher-0.2.5
[0.2.4]: https://github.com/bluesabre/sgt-launcher/compare/sgt-launcher-0.2.3...sgt-launcher-0.2.4
[0.2.3]: https://github.com/bluesabre/sgt-launcher/compare/sgt-launcher-0.2.2...sgt-launcher-0.2.3
[0.2.2]: https://github.com/bluesabre/sgt-launcher/compare/sgt-launcher-0.2.1...sgt-launcher-0.2.2
[0.2.1]: https://github.com/bluesabre/sgt-launcher/compare/sgt-launcher-0.2.0...sgt-launcher-0.2.1
[0.2.0]: https://github.com/bluesabre/sgt-launcher/compare/sgt-launcher-0.1.0...sgt-launcher-0.2.0
[0.1.0]: https://github.com/bluesabre/sgt-launcher/releases/tag/sgt-launcher-0.1.0