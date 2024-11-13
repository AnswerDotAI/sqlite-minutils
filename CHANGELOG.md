# Release notes

## 4.0.2

### Bugs fixed

- execute does not work with named params


## 4.0.1

### Bugs fixed

- Handle empty updates correctly


## 4.0.0

### New Features

- NB: We are no longing basing our version numbers on sqlite-minutils, so we have bumped the major version number
- Add `db.fetchone`


## 3.37.0.post4

### Breaking changes

- Use explicit transactions ([#19](https://github.com/AnswerDotAI/sqlite-minutils/issues/19))


## 3.37.0.post3

### New Features

- Cleaner error handling on offset without limit ([#11](https://github.com/AnswerDotAI/sqlite-minutils/pull/11)), thanks to [@pydanny](https://github.com/pydanny)
- Correct `Database.create_table` to support transforms. ([#9](https://github.com/AnswerDotAI/sqlite-minutils/pull/9)), thanks to [@pydanny](https://github.com/pydanny)


## 3.37.0.post2

### New Features

- add markdown to doc output ([#8](https://github.com/AnswerDotAI/sqlite-minutils/issues/8))
- Support list foreign keys in `db.t.create()` ([#6](https://github.com/AnswerDotAI/sqlite-minutils/pull/6)), thanks to [@minki-j](https://github.com/minki-j)
- Add `select` param ([#4](https://github.com/AnswerDotAI/sqlite-minutils/issues/4))
- Adding __contains__ to table ([#3](https://github.com/AnswerDotAI/sqlite-minutils/pull/3)), thanks to [@johnowhitaker](https://github.com/johnowhitaker)
- Retain indexes when calling transform ([#1](https://github.com/AnswerDotAI/sqlite-minutils/pull/1)), thanks to [@matdmiller](https://github.com/matdmiller)


