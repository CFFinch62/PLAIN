package runtime

import (
	"os"
	"path/filepath"
	"testing"
)

// TestSimpleFileOps tests simple file read/write operations
func TestSimpleFileOps(t *testing.T) {
	builtins := GetBuiltins()
	tmpFile := filepath.Join(os.TempDir(), "plain_test_simple.txt")
	defer os.Remove(tmpFile)

	// write_file
	result := builtins["write_file"].Fn(NewString(tmpFile), NewString("Hello, Test!"))
	if _, ok := result.(*ErrorValue); ok {
		t.Errorf("write_file failed: %s", result.String())
	}

	// read_file
	result = builtins["read_file"].Fn(NewString(tmpFile))
	if str, ok := result.(*StringValue); ok {
		if str.Val != "Hello, Test!" {
			t.Errorf("read_file got %s, want 'Hello, Test!'", str.Val)
		}
	} else {
		t.Errorf("read_file failed: %s", result.String())
	}

	// append_file
	builtins["append_file"].Fn(NewString(tmpFile), NewString("\nMore text"))
	result = builtins["read_file"].Fn(NewString(tmpFile))
	if str, ok := result.(*StringValue); ok {
		if str.Val != "Hello, Test!\nMore text" {
			t.Errorf("append_file failed, got %s", str.Val)
		}
	}
}

// TestReadWriteLines tests line-based file operations
func TestReadWriteLines(t *testing.T) {
	builtins := GetBuiltins()
	tmpFile := filepath.Join(os.TempDir(), "plain_test_lines.txt")
	defer os.Remove(tmpFile)

	lines := &ListValue{Elements: []Value{
		NewString("Line 1"),
		NewString("Line 2"),
		NewString("Line 3"),
	}}

	builtins["write_lines"].Fn(NewString(tmpFile), lines)
	result := builtins["read_lines"].Fn(NewString(tmpFile))
	if lst, ok := result.(*ListValue); ok {
		if len(lst.Elements) != 3 {
			t.Errorf("read_lines got %d lines, want 3", len(lst.Elements))
		}
	} else {
		t.Errorf("read_lines failed: %s", result.String())
	}
}

// TestBinaryOps tests binary file operations
func TestBinaryOps(t *testing.T) {
	builtins := GetBuiltins()
	tmpFile := filepath.Join(os.TempDir(), "plain_test_binary.bin")
	defer os.Remove(tmpFile)

	data := &BytesValue{Data: []byte{0x00, 0x01, 0x02, 0xFF}}
	builtins["write_binary"].Fn(NewString(tmpFile), data)

	result := builtins["read_binary"].Fn(NewString(tmpFile))
	if bytes, ok := result.(*BytesValue); ok {
		if len(bytes.Data) != 4 {
			t.Errorf("read_binary got %d bytes, want 4", len(bytes.Data))
		}
	} else {
		t.Errorf("read_binary failed: %s", result.String())
	}
}

// TestFileHandles tests handle-based file operations
func TestFileHandles(t *testing.T) {
	builtins := GetBuiltins()
	tmpFile := filepath.Join(os.TempDir(), "plain_test_handle.txt")
	defer os.Remove(tmpFile)

	// open for write
	handle := builtins["open"].Fn(NewString(tmpFile), NewString("w"))
	if _, ok := handle.(*FileHandleValue); !ok {
		t.Fatalf("open failed: %s", handle.String())
	}

	// write
	builtins["write_line"].Fn(handle, NewString("Test line"))
	builtins["close"].Fn(handle)

	// open for read
	handle = builtins["open"].Fn(NewString(tmpFile), NewString("r"))
	if _, ok := handle.(*FileHandleValue); !ok {
		t.Fatalf("open for read failed: %s", handle.String())
	}

	content := builtins["read"].Fn(handle)
	builtins["close"].Fn(handle)

	if str, ok := content.(*StringValue); ok {
		if str.Val != "Test line\n" {
			t.Errorf("read got %q, want 'Test line\\n'", str.Val)
		}
	}
}

// TestFileSystemOps tests file system operations
func TestFileSystemOps(t *testing.T) {
	builtins := GetBuiltins()
	tmpFile := filepath.Join(os.TempDir(), "plain_test_fs.txt")
	defer os.Remove(tmpFile)

	// file_exists (should be false)
	result := builtins["file_exists"].Fn(NewString(tmpFile))
	if b := result.(*BooleanValue); b.Val {
		t.Error("file_exists returned true for non-existent file")
	}

	// create file
	builtins["write_file"].Fn(NewString(tmpFile), NewString("test"))

	// file_exists (should be true)
	result = builtins["file_exists"].Fn(NewString(tmpFile))
	if b := result.(*BooleanValue); !b.Val {
		t.Error("file_exists returned false for existing file")
	}

	// file_size
	result = builtins["file_size"].Fn(NewString(tmpFile))
	if size, ok := result.(*IntegerValue); ok {
		if size.Val != 4 {
			t.Errorf("file_size got %d, want 4", size.Val)
		}
	}

	// copy_file
	tmpCopy := tmpFile + ".copy"
	defer os.Remove(tmpCopy)
	builtins["copy_file"].Fn(NewString(tmpFile), NewString(tmpCopy))
	if b := builtins["file_exists"].Fn(NewString(tmpCopy)).(*BooleanValue); !b.Val {
		t.Error("copy_file didn't create copy")
	}

	// rename_file
	tmpRenamed := tmpFile + ".renamed"
	defer os.Remove(tmpRenamed)
	builtins["rename_file"].Fn(NewString(tmpCopy), NewString(tmpRenamed))
	if b := builtins["file_exists"].Fn(NewString(tmpRenamed)).(*BooleanValue); !b.Val {
		t.Error("rename_file failed")
	}
}

// TestDirOps tests directory operations
func TestDirOps(t *testing.T) {
	builtins := GetBuiltins()
	tmpDir := filepath.Join(os.TempDir(), "plain_test_dir")
	defer os.RemoveAll(tmpDir)

	// dir_exists (should be false)
	result := builtins["dir_exists"].Fn(NewString(tmpDir))
	if b := result.(*BooleanValue); b.Val {
		t.Error("dir_exists returned true for non-existent dir")
	}

	// create_dir
	builtins["create_dir"].Fn(NewString(tmpDir))

	// dir_exists (should be true)
	result = builtins["dir_exists"].Fn(NewString(tmpDir))
	if b := result.(*BooleanValue); !b.Val {
		t.Error("dir_exists returned false for existing dir")
	}

	// list_dir
	result = builtins["list_dir"].Fn(NewString(os.TempDir()))
	if _, ok := result.(*ListValue); !ok {
		t.Errorf("list_dir failed: %s", result.String())
	}

	// delete_dir
	builtins["delete_dir"].Fn(NewString(tmpDir))
	result = builtins["dir_exists"].Fn(NewString(tmpDir))
	if b := result.(*BooleanValue); b.Val {
		t.Error("delete_dir didn't remove directory")
	}
}

// TestPathOps tests path operations
func TestPathOps(t *testing.T) {
	builtins := GetBuiltins()

	// join_path
	result := builtins["join_path"].Fn(NewString("a"), NewString("b"), NewString("c.txt"))
	if str := result.(*StringValue); str.Val != filepath.Join("a", "b", "c.txt") {
		t.Errorf("join_path got %s", str.Val)
	}

	// split_path
	result = builtins["split_path"].Fn(NewString("/home/user/file.txt"))
	if lst := result.(*ListValue); len(lst.Elements) != 2 {
		t.Errorf("split_path got %d elements, want 2", len(lst.Elements))
	}

	// get_extension
	result = builtins["get_extension"].Fn(NewString("file.txt"))
	if str := result.(*StringValue); str.Val != ".txt" {
		t.Errorf("get_extension got %s, want .txt", str.Val)
	}

	// absolute_path
	result = builtins["absolute_path"].Fn(NewString("."))
	if _, ok := result.(*StringValue); !ok {
		t.Errorf("absolute_path failed: %s", result.String())
	}

	// script_dir
	SetScriptDirectory("/test/script/dir")
	result = builtins["script_dir"].Fn()
	if str, ok := result.(*StringValue); !ok {
		t.Errorf("script_dir failed: %s", result.String())
	} else if !filepath.IsAbs(str.Val) {
		t.Errorf("script_dir should return absolute path, got: %s", str.Val)
	}
}

// TestFileIOErrors tests error handling
func TestFileIOErrors(t *testing.T) {
	builtins := GetBuiltins()

	// read non-existent file
	result := builtins["read_file"].Fn(NewString("/nonexistent/path/to/file.txt"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("read_file should error for non-existent file")
	}

	// invalid open mode
	result = builtins["open"].Fn(NewString("test.txt"), NewString("invalid"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("open should error for invalid mode")
	}
}
