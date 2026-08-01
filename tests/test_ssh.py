from ccmd.core.ssh import SSHHost, SSHStore


def test_ssh_argv_no_shell(ccmd_home) -> None:
    h = SSHHost(id="sage", host="10.0.0.1", user="dec", port=22, identity_file="~/.ssh/id_ed25519")
    argv = h.build_ssh_argv()
    assert argv[0] == "ssh"
    assert "-i" in argv
    assert "dec@10.0.0.1" in argv


def test_ssh_store(ccmd_home) -> None:
    store = SSHStore()
    store.upsert(SSHHost(id="box", host="example.com", user="u"))
    assert store.get("box") is not None
    assert store.delete("box")
