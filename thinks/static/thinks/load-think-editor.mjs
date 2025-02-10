import './code-editor.mjs';

export default async function init_app() {
    const flags = JSON.parse(document.getElementById('think-editor-data').textContent);
    const packages = await (await fetch('https://elm-package-list.think.somethingorotherwhatever.com/elm-packages.json')).json();
    flags.elm_packages = packages;
    flags.csrf_token = document.getElementById('csrftoken')?.textContent || '';
    const app = Elm.App.init({node: document.body, flags});

    app.ports.reload_preview.subscribe(() => {
        console.log('reload preview');
        const iframe = document.getElementById('preview-frame');
        if(iframe) {
            const src = iframe.src;
            iframe.src = "";
            setTimeout(() => {
                iframe.src = src;
            },10);
        }
    })

    app.ports.show_modal.subscribe(id => {
      console.log(id);
      document.getElementById(id).showModal()
    })
}