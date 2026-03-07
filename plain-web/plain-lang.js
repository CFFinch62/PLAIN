// Monaco language definition for PLAIN
// Loaded as a plain <script> before app.js; attaches to window.
// Called inside the require(["vs/editor/editor.main"], ...) callback.

window.registerPlainLanguage = function registerPlainLanguage(monaco) {
  monaco.languages.register({ id: "plain" });

  monaco.languages.setMonarchTokensProvider("plain", {
    defaultToken: "",
    tokenPostfix: ".plain",

    // ── Keywords ────────────────────────────────────────────────
    keywords: [
      "task", "with", "using", "deliver", "abort", "swap",
      "var", "fxd", "as",
      "if", "then", "else", "choose", "choice", "default",
      "loop", "from", "to", "step", "in", "exit", "continue",
      "attempt", "handle", "ensure",
      "record", "based", "on",
      "and", "or", "not",
      "true", "false", "null",
    ],

    typeKeywords: [
      "integer", "float", "string", "boolean", "list", "table", "of",
      "int", "flt", "str", "bln", "lst", "tbl",
    ],

    builtins: [
      "display", "get", "clear",
      "to_string", "to_int", "to_float", "to_bool",
      "len", "type_of", "range",
      "abs", "round", "floor", "ceil", "min", "max", "sum", "power",
      "random", "random_int",
      "append", "prepend", "remove", "remove_at", "insert",
      "contains", "index_of", "reverse", "sort", "slice",
      "keys", "values", "has_key", "remove_key",
      "split", "join", "trim", "upper", "lower",
      "starts_with", "ends_with", "replace", "substring",
      "char_at", "char_code", "from_char_code",
      "format", "pad_left", "pad_right",
      "now", "wait", "sleep", "time", "date",
      "read_file", "write_file", "append_file",
      "open", "close", "read", "write",
    ],

    operators: [
      "=", "+=", "-=", "*=", "/=", "%=", "&=",
      "+", "-", "*", "/", "//", "%", "**",
      "==", "!=", "<", ">", "<=", ">=",
      "&",
    ],

    // ── Tokeniser rules ─────────────────────────────────────────
    tokenizer: {
      root: [
        // Comments: rem: ... and note: ...
        [/^[ \t]*(rem:|note:).*$/, "comment"],

        // Interpolated strings v"..."
        [/v"/, { token: "string.quote", next: "@vstring" }],

        // Regular strings
        [/"/, { token: "string.quote", next: "@string" }],

        // Numbers
        [/\b\d+\.\d+\b/, "number.float"],
        [/\b\d+\b/,      "number"],

        // Whitespace
        [/[ \t]+/, "white"],

        // Identifiers, keywords, builtins
        [/[a-zA-Z_][a-zA-Z0-9_]*/, {
          cases: {
            "@keywords":     "keyword",
            "@typeKeywords": "type",
            "@builtins":     "predefined",
            "@default":      "identifier",
          }
        }],

        // Operators
        [/\/\/|[+\-*/%]=?|\*\*|==|!=|<=|>=|[<>=&]/, "operator"],

        // Delimiters
        [/[()[\]{},.:]/,  "delimiter"],
      ],

      string: [
        [/[^"\\]+/, "string"],
        [/\\./,     "string.escape"],
        [/"/,       { token: "string.quote", next: "@pop" }],
      ],

      vstring: [
        [/[^"{\\]+/, "string"],
        [/\{[^}]*\}/, "string.template"],
        [/\\./,       "string.escape"],
        [/"/,         { token: "string.quote", next: "@pop" }],
      ],
    },
  });

  // ── Theme colours (Catppuccin-inspired) ───────────────────────
  monaco.editor.defineTheme("plain-dark", {
    base: "vs-dark",
    inherit: true,
    rules: [
      { token: "comment",         foreground: "6c7086", fontStyle: "italic" },
      { token: "keyword",         foreground: "cba6f7", fontStyle: "bold" },
      { token: "type",            foreground: "94e2d5" },
      { token: "predefined",      foreground: "89b4fa" },
      { token: "string",          foreground: "a6e3a1" },
      { token: "string.quote",    foreground: "a6e3a1" },
      { token: "string.template", foreground: "f9e2af" },
      { token: "string.escape",   foreground: "fab387" },
      { token: "number",          foreground: "fab387" },
      { token: "number.float",    foreground: "fab387" },
      { token: "operator",        foreground: "89dceb" },
      { token: "delimiter",       foreground: "cdd6f4" },
      { token: "identifier",      foreground: "cdd6f4" },
    ],
    colors: {
      "editor.background":           "#1e1e2e",
      "editor.foreground":           "#cdd6f4",
      "editorLineNumber.foreground": "#45475a",
      "editorCursor.foreground":     "#cba6f7",
      "editor.selectionBackground":  "#45475a88",
      "editor.lineHighlightBackground": "#31324466",
      "editorIndentGuide.background1": "#31324488",
    },
  });
}

