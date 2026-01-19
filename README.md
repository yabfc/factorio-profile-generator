Create a dump by adding `--dump-data` to the Factorio Launch Options in Steam.
The dump will be produced in `~/.factorio/script-output`

```sh
git clone git@github.com:yabfc/factorio-profile-generator.git
cd factorio-profile-generator
uv sync
uv run main.py <your-dump.json> -o 
```

### Acknowledgements

- @jacquev6 ([factorio-data-raw-json-schema](https://github.com/jacquev6/factorio-data-raw-json-schema)) - source for the generated pydantic model
