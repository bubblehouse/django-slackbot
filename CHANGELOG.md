## [1.3.1](https://github.com/bubblehouse/django-slackbot/compare/v1.3.0...v1.3.1) (2026-05-22)

### Bug Fixes

* allow chat module to import without SLACK_BOT_TOKEN configured ([1706714](https://github.com/bubblehouse/django-slackbot/commit/1706714028b8d1b18f64fae9df1cd95f6cca90aa))

## [1.3.0](https://github.com/bubblehouse/django-slackbot/compare/v1.2.0...v1.3.0) (2026-05-21)

### Features

* **scheduler:** replace in-process scheduler with celery worker + beat ([c28682f](https://github.com/bubblehouse/django-slackbot/commit/c28682fc753c864b8528dfb8c5e60cd04c08238c))

### Bug Fixes

* **frinkiac:** narrow color/font types so mypy stops complaining ([6912aa7](https://github.com/bubblehouse/django-slackbot/commit/6912aa7632128c77b18fb2ea9410a839ef8a46bb))
* **frinkiac:** retarget meme rendering at /comic/img binary payload endpoint ([be47bb6](https://github.com/bubblehouse/django-slackbot/commit/be47bb64563e96637d103e0002c0de952b4a36c6))

## [1.2.0](https://github.com/bubblehouse/django-slackbot/compare/v1.1.4...v1.2.0) (2026-05-21)

### Features

* **types:** add type annotations to chat handlers and management commands ([43ec44c](https://github.com/bubblehouse/django-slackbot/commit/43ec44c63af5986b48e0d8b811304b8462ca8437))

### Bug Fixes

* **docker:** relocate venv to /usr/app/venv to avoid WORKDIR collision ([edf2e7c](https://github.com/bubblehouse/django-slackbot/commit/edf2e7cb04d2c3d7d6d92398594b87c85acef436))

## [1.1.4](https://github.com/bubblehouse/django-slackbot/compare/v1.1.3...v1.1.4) (2025-02-13)

### Bug Fixes

* improve error handling for unhandled requests ([3f25ec3](https://github.com/bubblehouse/django-slackbot/commit/3f25ec3ef13d89519fa47c8c38149dcd5ff413f5))

## [1.1.3](https://github.com/bubblehouse/django-slackbot/compare/v1.1.2...v1.1.3) (2025-02-13)

### Bug Fixes

* improve error handling for unhandled requests ([a07a737](https://github.com/bubblehouse/django-slackbot/commit/a07a737d198650169242060ec07f6669e39eb0a2))

## [1.1.2](https://github.com/bubblehouse/django-slackbot/compare/v1.1.1...v1.1.2) (2025-02-13)

### Bug Fixes

* improve error handling for unhandled requests ([479234c](https://github.com/bubblehouse/django-slackbot/commit/479234ce28b0c7c494524a3d3107e7915d808b84))

## [1.1.1](https://github.com/philchristensen/django-slackbot/compare/v1.1.0...v1.1.1) (2024-10-20)

### Bug Fixes

* include optional packages in tarball ([fc50cf5](https://github.com/philchristensen/django-slackbot/commit/fc50cf51010138feb13ef6f053e7651651b81547))
* typo ([a70cbc5](https://github.com/philchristensen/django-slackbot/commit/a70cbc5efd04b162f961c1b60a874b37569c94b6))

## [1.1.0](https://github.com/philchristensen/django-slackbot/compare/v1.0.11...v1.1.0) (2024-10-20)

### Features

* move optional chat features into dedicated apps ([ca893a3](https://github.com/philchristensen/django-slackbot/commit/ca893a34c40dc3b3ba7f5144a653a142e6ebaaca))

## [1.0.11](https://github.com/philchristensen/django-slackbot/compare/v1.0.10...v1.0.11) (2024-10-19)

### Bug Fixes

* include management commands in the library package ([b5883f7](https://github.com/philchristensen/django-slackbot/commit/b5883f7337917bdee8c6da107e7ab4af3653373e))

## [1.0.10](https://github.com/philchristensen/django-slackbot/compare/v1.0.9...v1.0.10) (2024-10-08)

### Bug Fixes

* remove unneded cruft ([5772307](https://github.com/philchristensen/django-slackbot/commit/57723078788d6c6031c857b698207d74fc1cc742))

## [1.0.9](https://github.com/philchristensen/django-slackbot/compare/v1.0.8...v1.0.9) (2024-10-08)

### Bug Fixes

* various bugfixes to deployment test ([636a353](https://github.com/philchristensen/django-slackbot/commit/636a353bda917ddab6541781408a825cb7b94200))

## [1.0.8](https://github.com/philchristensen/django-slackbot/compare/v1.0.7...v1.0.8) (2024-10-08)

### Bug Fixes

* typo ([afbf583](https://github.com/philchristensen/django-slackbot/commit/afbf58394a4cb10abcb28488c3e00f1b9febebe2))

## [1.0.7](https://github.com/philchristensen/django-slackbot/compare/v1.0.6...v1.0.7) (2024-10-07)

### Bug Fixes

* force a new release ([0a16eaf](https://github.com/philchristensen/django-slackbot/commit/0a16eaf3082a5a709d78d6055c0c85c6e85ccaaf))

## [1.0.6](https://github.com/philchristensen/django-slackbot/compare/v1.0.5...v1.0.6) (2024-10-04)

### Bug Fixes

* update pyproject.toml version ([3210639](https://github.com/philchristensen/django-slackbot/commit/32106390716717f00a67b118886cb901aaad1e70))

## [1.0.5](https://github.com/philchristensen/django-slackbot/compare/v1.0.4...v1.0.5) (2024-10-04)

### Bug Fixes

* update pyproject.toml version ([a8c9b35](https://github.com/philchristensen/django-slackbot/commit/a8c9b35de509251f80036e3df518d4c4a1c8da89))

## [1.0.4](https://github.com/philchristensen/django-slackbot/compare/v1.0.3...v1.0.4) (2024-10-04)

### Bug Fixes

* rename app, already taken ([16c4d49](https://github.com/philchristensen/django-slackbot/commit/16c4d49dde9059cf42e49a9b3540241f5ea17261))

## [1.0.3](https://github.com/philchristensen/django-slackbot/compare/v1.0.2...v1.0.3) (2024-10-04)

### Bug Fixes

* rename app, already taken ([4a1a7a8](https://github.com/philchristensen/django-slackbot/commit/4a1a7a86f328c8dce9bb3ddba9488a18b876edea))

## [1.0.2](https://github.com/philchristensen/django-slackbot/compare/v1.0.1...v1.0.2) (2024-10-04)

### Bug Fixes

* rename app, already taken ([235dad7](https://github.com/philchristensen/django-slackbot/commit/235dad7aa764431b60883c8ec2b2aed7b927d8cc))
* rename app, already taken ([c112334](https://github.com/philchristensen/django-slackbot/commit/c112334792d7436a0a5ef76234dd301448f7b62b))

## [1.0.1](https://github.com/philchristensen/django-slack-bot/compare/v1.0.0...v1.0.1) (2024-10-04)

### Bug Fixes

* rename app, already taken ([70a3991](https://github.com/philchristensen/django-slack-bot/commit/70a3991fa4ad3ca764ee856168a34b9c19f6af3e))

## 1.0.0 (2024-10-04)

### Bug Fixes

* force a new release ([012525f](https://github.com/philchristensen/django-slack/commit/012525f3d71c8cbd705ce1560e5b1c6f31e8ec69))
