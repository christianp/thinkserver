NODE_BIN=node_modules/.bin

DEST=../thinks/static/thinks

$(DEST)/code-editor.mjs: code-editor.bundle.mjs
	cp $< $@

code-editor.terser.mjs: code-editor.bundle.mjs
	$(NODE_BIN)/terser --compress --mangle -- $< > $@

code-editor.bundle.mjs: code-editor.mjs
	$(NODE_BIN)/rollup $< -f es -p @rollup/plugin-node-resolve -o $@

