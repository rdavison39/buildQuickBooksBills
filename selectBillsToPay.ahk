; Press Space then Down repeatedly
; ESC to stop
; =========================================
; ESC - Stop Immediately
; =========================================
Esc::
StopProcessing := true
running := false
Return

running := false

F2::
running := true
Loop
{
    if (!running)
        break

    Send {Space}
    Sleep 50

    Send {Down}
    Sleep 50
}

