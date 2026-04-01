; ==================================================
; processVendor.ahk
; Processes all bills for current vendor
; ==================================================

ProcessVendor()
{
    ; Focus first bill
    Click 1603, 783
    Sleep 400

    Loop
    {
        ; Open bill
        Send {Enter}
        Sleep 1500

        ; Process bill
        ProcessBill()

        ; Move to next bill
        Send {Down}
        Sleep 200

        ; Try open next bill
        Send {Enter}
        Sleep 1200

        ; Detect if no more bills
        WinGetTitle, title, A

        if !InStr(title, "Bill")
            break
    }
}