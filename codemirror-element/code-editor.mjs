import {basicSetup} from "codemirror";
import {EditorView, keymap} from "@codemirror/view";
import {EditorState} from "@codemirror/state";
import {python} from "@codemirror/lang-python";
import {r} from "codemirror-lang-r";
import {vim} from "@replit/codemirror-vim";
import {indentWithTab} from "@codemirror/commands";

window.EditorView = EditorView;

const languages = {
    'python': python,
    'r': r
}

export function codemirror_editor(language, options) {
    const language_plugin = languages[language];

    options = Object.assign({
        extensions: [
            vim(),
            basicSetup,
            keymap.of([indentWithTab]),
            EditorView.updateListener.of(update => {
                if(!options?.onChange || update.changes.desc.empty) {
                    return;
                }
                options.onChange(update);
            })
        ]
    }, options);

    let editor = new EditorView(options);

    return editor;
}


export class CodeEditorElement extends HTMLElement {
    constructor() {
        super();

        this.language = this.getAttribute('language') || '';
        const shadowRoot = this.attachShadow({mode: 'open'});
    }

    connectedCallback() {
        this.init_editor();
    }

    init_editor() {
        const code = this.textContent;
        const code_tag = this.shadowRoot;

        this.codeMirror = codemirror_editor(
            this.language,
            {
                doc: code,
                parent: code_tag,
                root: this.shadowRoot,
                onChange: update => this.onChange(update)
            }
        );
    }

    onChange() {
        const code = this.codeMirror.state.doc.toString();
        this.value = code;
        this.dispatchEvent(new CustomEvent('change'));
    }
}

customElements.define("code-editor", CodeEditorElement);
