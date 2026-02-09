// ----------------------------------------------------------------------------
// \file  dBaseRuntime.js
// \note  (c) 2025, 2026 by Jens Kallup - paule32
//        all rights reserved.
// ----------------------------------------------------------------------------
export function WRITE(...args) {
    if (args.length === 0) console.log();
    else args.forEach(a => console.log(a));
}

export function NEWOBJ(className, ...args) {
    const cn = String(className || "").toUpperCase();
    switch (cn) {
        case "PUSHBUTTON":
            return new PushButton(...args);
        default:
            throw new Error(`RT.NEWOBJ: Unbekannte Klasse: ${className}`);
    }
}

// Mini-Basis + Beispielklasse
export class ParentForm {
    Init() {}
}

export class PushButton {
    constructor(text = "") {
        this.Text = text;
    }
    
    toString() {
        return `PushButton(Text='${this.Text}')`;
    }
}
