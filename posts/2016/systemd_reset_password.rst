Reset Password in Systemd
#########################

:date: 2016-08-28 10:00:00
:tag: Linux, Systemd

现在基本是用 ssh key 来登录系统了。之前可以直接在 GRUB 直接进单用户改密码。使用了 systemd 的系统，后已经不可以这么使用了。原因是 Systemd 的单用户模式使用了 ``/usr/sbin/sulogin`` 这个 shell, 也必须输入密码才可以。

::

    # /usr/lib/systemd/system/rescue.service
    [Unit]
    Description=Rescue Shell
    Documentation=man:sulogin(8)
    DefaultDependencies=no
    Conflicts=shutdown.target
    After=sysinit.target plymouth-start.service
    Before=shutdown.target

    [Service]
    Environment=HOME=/root
    WorkingDirectory=-/root
    ExecStartPre=-/bin/plymouth --wait quit
    ExecStartPre=-/bin/echo -e 'You are in rescue mode. After logging in, type "journalctl -xb" to view\\nsystem logs, "systemctl reboot" to reboot, "systemctl default" or ^D to\\nboot into default mode.'
    ExecStart=-/bin/sh -c "/usr/bin/sulogin; /usr/bin/systemctl --job-mode=fail --no-block default"
    Type=idle
    StandardInput=tty-force
    StandardOutput=inherit
    StandardError=inherit
    KillMode=process
    IgnoreSIGPIPE=no
    SendSIGHUP=yes


自 systemd 215 版本后，新加了一个 ``systemd.debug-shell`` 的内核参数，内容如下：

::

    # /usr/lib/systemd/system/debug-shell.service
    [Unit]
    Description=Early root shell on /dev/tty9 FOR DEBUGGING ONLY
    Documentation=man:sushell(8)
    DefaultDependencies=no
    IgnoreOnIsolate=yes
    ConditionPathExists=/dev/tty9

    [Service]
    Environment=TERM=linux
    ExecStart=/bin/sh
    Restart=always
    RestartSec=0
    StandardInput=tty
    TTYPath=/dev/tty9
    TTYReset=yes
    TTYVHangup=yes
    KillMode=process
    IgnoreSIGPIPE=no
    # bash ignores SIGTERM
    KillSignal=SIGHUP

    # Unset locale for the console getty since the console has problems
    # displaying some internationalized messages.
    Environment=LANG= LANGUAGE= LC_CTYPE= LC_NUMERIC= LC_TIME= LC_COLLATE= LC_MONETARY= LC_MESSAGES= LC_PAPER= LC_NAME= LC_ADDRESS= LC_TELEPHONE= LC_MEASUREMENT= LC_IDENTIFICATION=

    [Install]
    WantedBy=sysinit.target

可以看到，systemd 直接在 ``tty9`` 上面开了一个 sh, 不用密码就可以登录。

使用方法很简单，在 GRUB 界面上，输入 ``e`` 进入编辑模式，找到 ``linux16`` 那一行，在后面加入 ``systemd.debug-shell`` 就可以了。之后 ``Ctrl + x`` 继续启动就可以了。启动完成后，``Ctrl + Alt + F9`` 进入 ``tty9``， 就可以欢快的改密码了
