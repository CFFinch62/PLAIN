// PLAIN Language extension -- run/analyze/REPL commands for .plain files.
//
// Syntax highlighting, snippets and editor behaviours are entirely declarative
// (package.json + the grammar + language-configuration.json) and do not need
// this file. Everything here drives the `plain` interpreter.

const vscode = require('vscode');
const cp = require('child_process');
const path = require('path');

// PLAIN reports diagnostics in two different shapes, and the file they belong
// to appears only on a preceding header line (cmd/plain/main.go):
//
//   Parser errors for: /path/to/file.plain
//   =====================================
//   ERROR: Expected next token to be RPAREN, got NEWLINE instead (line 1, column 10)
//
//   Semantic errors for: /path/to/file.plain
//   =====================================
//   ERROR: line 3, column 4: variable 'x' already declared at line 2
//
// Runtime failures print `Runtime error: <msg>` with no position at all.
const HEADER_RE = /^(?:Parser|Semantic) errors for:\s*(.*)$/;
const TRAILING_POS_RE = /^ERROR:\s+(.*)\s+\(line (\d+), column (\d+)\)$/;
const LEADING_POS_RE = /^ERROR:\s+line (\d+), column (\d+):\s+(.*)$/;

let diagnostics = null;
let output = null;

function config() {
  return vscode.workspace.getConfiguration('plain');
}

function interpreter() {
  return config().get('interpreterPath', 'plain') || 'plain';
}

/** Extra CLI args common to every invocation. */
function commonArgs(doc) {
  const root = (config().get('projectRoot', '') || '').trim();
  if (!root) return [];
  const folder = vscode.workspace.getWorkspaceFolder(doc.uri);
  const resolved = root.replace(
    /\$\{workspaceFolder\}/g,
    folder ? folder.uri.fsPath : path.dirname(doc.fileName)
  );
  return [`--project-root=${resolved}`];
}

function shellQuote(p) {
  if (process.platform === 'win32') return `"${p}"`;
  return `'${p.replace(/'/g, `'\\''`)}'`;
}

async function activePlainDocument() {
  const editor = vscode.window.activeTextEditor;
  if (!editor || editor.document.languageId !== 'plain') {
    vscode.window.showErrorMessage('PLAIN: no .plain file is active.');
    return null;
  }
  if (config().get('saveBeforeRun', true) && editor.document.isDirty) {
    await editor.document.save();
  }
  return editor.document;
}

function runInTerminal(doc, extraArgs) {
  let term = vscode.window.terminals.find((t) => t.name === 'PLAIN');
  if (!term) {
    term = vscode.window.createTerminal({
      name: 'PLAIN',
      cwd: path.dirname(doc.fileName),
    });
  }
  term.show(true);
  const parts = [
    shellQuote(interpreter()),
    ...extraArgs.map(shellQuote),
    shellQuote(doc.fileName),
  ];
  term.sendText(parts.join(' '));
}

function runInOutputChannel(doc, extraArgs) {
  if (!output) output = vscode.window.createOutputChannel('PLAIN');
  output.clear();
  output.show(true);

  const exe = interpreter();
  const args = [...extraArgs, doc.fileName];
  output.appendLine(`> ${exe} ${args.join(' ')}`);
  output.appendLine('');

  const started = Date.now();
  const child = cp.spawn(exe, args, { cwd: path.dirname(doc.fileName) });

  // PLAIN writes its diagnostics with fmt.Printf, i.e. to stdout rather than
  // stderr, so stdout is what has to be scanned. stderr is still captured in
  // case the process dies some other way.
  let combined = '';
  child.stdout.on('data', (d) => {
    const text = d.toString();
    combined += text;
    output.append(text);
  });
  child.stderr.on('data', (d) => {
    const text = d.toString();
    combined += text;
    output.append(text);
  });

  child.on('error', (err) => {
    if (err.code === 'ENOENT') {
      vscode.window
        .showErrorMessage(
          `PLAIN: interpreter '${exe}' not found. Set plain.interpreterPath to the built binary.`,
          'Open Settings'
        )
        .then((choice) => {
          if (choice === 'Open Settings') {
            vscode.commands.executeCommand(
              'workbench.action.openSettings',
              'plain.interpreterPath'
            );
          }
        });
    } else {
      vscode.window.showErrorMessage(`PLAIN: ${err.message}`);
    }
  });

  child.on('close', (code) => {
    publishDiagnostics(doc, combined);
    output.appendLine('');
    output.appendLine(
      `[exit ${code} in ${((Date.now() - started) / 1000).toFixed(2)}s]`
    );
  });
}

/** Scan interpreter output for diagnostics and turn them into squiggles.
 *  The file comes from the most recent header line; failing that, the document
 *  that was run. Runtime errors carry no position and are deliberately left in
 *  the Output channel rather than pinned to an arbitrary line. */
function publishDiagnostics(doc, text) {
  const byFile = new Map();
  let currentFile = doc.fileName;

  const add = (file, line, column, message) => {
    // PLAIN reports 1-based lines; its columns are already 0-based (the lexer
    // resets column to 0 at each newline), so only the line is adjusted.
    const pos = new vscode.Position(
      Math.max(0, parseInt(line, 10) - 1),
      Math.max(0, parseInt(column, 10))
    );
    const uri = vscode.Uri.file(path.resolve(path.dirname(doc.fileName), file));
    const diag = new vscode.Diagnostic(
      new vscode.Range(pos, pos),
      message,
      vscode.DiagnosticSeverity.Error
    );
    diag.source = 'plain';
    const key = uri.toString();
    if (!byFile.has(key)) byFile.set(key, { uri, items: [] });
    byFile.get(key).items.push(diag);
  };

  for (const raw of text.split('\n')) {
    const line = raw.trimEnd();

    const header = HEADER_RE.exec(line);
    if (header) {
      currentFile = header[1].trim();
      continue;
    }

    // Semantic shape is checked first: it also starts with `ERROR: `, but its
    // position comes before the message rather than after it.
    const leading = LEADING_POS_RE.exec(line);
    if (leading) {
      add(currentFile, leading[1], leading[2], leading[3]);
      continue;
    }

    const trailing = TRAILING_POS_RE.exec(line);
    if (trailing) {
      add(currentFile, trailing[2], trailing[3], trailing[1]);
    }
  }

  diagnostics.clear();
  for (const { uri, items } of byFile.values()) {
    diagnostics.set(uri, items);
  }
}

async function run() {
  const doc = await activePlainDocument();
  if (!doc) return;
  const args = commonArgs(doc);
  if (config().get('runInTerminal', true)) runInTerminal(doc, args);
  else runInOutputChannel(doc, args);
}

/** `plain -analyze` type-checks without executing, so it always goes through
 *  the Output channel path regardless of the runInTerminal setting -- the
 *  whole point of the command is to populate the Problems panel. */
async function analyze() {
  const doc = await activePlainDocument();
  if (!doc) return;
  runInOutputChannel(doc, ['-analyze', ...commonArgs(doc)]);
}

function startRepl() {
  const term = vscode.window.createTerminal({ name: 'PLAIN REPL' });
  term.show(true);
  term.sendText(`${shellQuote(interpreter())} -repl`);
}

function activate(context) {
  diagnostics = vscode.languages.createDiagnosticCollection('plain');

  context.subscriptions.push(
    diagnostics,
    vscode.commands.registerCommand('plain.runFile', run),
    vscode.commands.registerCommand('plain.analyzeFile', analyze),
    vscode.commands.registerCommand('plain.startRepl', startRepl),
    vscode.workspace.onDidChangeTextDocument((e) => {
      if (e.document.languageId === 'plain') diagnostics.delete(e.document.uri);
    })
  );
}

function deactivate() {
  if (output) output.dispose();
}

module.exports = { activate, deactivate };
