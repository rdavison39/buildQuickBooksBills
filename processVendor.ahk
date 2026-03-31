#Include ProcessBill.ahk

; ==================================================
; ProcessVendor.ahk
; Always reset to first row then move down
; ==================================================

CoordMode, Mouse, Screen

F2::

row := 0

Loop
{
    ; --------------------------------------------------
    ; Always anchor to first row
    ; --------------------------------------------------
    Click 1603, 783
    Sleep 400

    ; --------------------------------------------------
    ; Move to desired row
    ; --------------------------------------------------
    Loop %row%
    {
        Send {Down}
        Sleep 150
    }

    ; --------------------------------------------------
    ; Try to open bill
    ; --------------------------------------------------
    Send {Enter}
    Sleep 1200

    ; --------------------------------------------------
    ; If bill didn't open, we are done
    ; (Window title changes when bill opens)
    ; --------------------------------------------------
    WinGetTitle, title, A

    if !InStr(title, "Bill")
    {
        
        break
    }

    ; --------------------------------------------------
    ; Process bill
    ; --------------------------------------------------
    ProcessBill()

    ; --------------------------------------------------
    ; Move to next bill
    ; --------------------------------------------------
    row++
}

Return

Esc::ExitApp