import * as GovspeakEditor from "govspeak-visual-editor";

export function initGovspeakVisualEditor() {
  const editor = new window.GovspeakVisualEditor(
    document.querySelector("#content"),
    document.querySelector("#editor"),
    document.querySelector("#govspeak")
  );

  editor.on("change", (event) => {
    console.log("change", event);
  });
}
