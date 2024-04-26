import './code-editor.mjs';

export default async function init_app() {
    const flags = JSON.parse(document.getElementById('think-editor-data').textContent);
    flags.csrf_token = document.getElementById('csrftoken')?.textContent || '';
    const app = Elm.App.init({node: document.body, flags});
}