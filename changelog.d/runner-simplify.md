### Changed

- The development validator runner dispatches leaves from one table and no longer re-validates installed schemas before running a helper, so it follows native `validate.py` behavior. New leaves wait until the desktop shell consumes the runner.
