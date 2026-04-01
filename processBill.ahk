; ==================================================
; processBill.ahk
; Process line items in bill
; ==================================================

ProcessBill()
{
    ; Move to Customer Job dropdown
    Loop 13
    {
        Send {Tab}
        Sleep 80
    }

    Sleep 500


    ; Loop through line items
    Loop
    {
        ; Open dropdown
        Send !{Down}
        Sleep 400

        ; Move to top
        Loop 6
        {
            Send {Up}
            Sleep 80
        }

        Sleep 200

        ; Search entries
        Loop 6
        {
            Send {Enter}
            Sleep 300

            clipboard := ""
            Send ^c
            ClipWait, .3

            if InStr(clipboard, "20961 Skyler")
                break

            Send !{Down}
            Sleep 200

            Send {Down}
            Sleep 150
        }

        ; Move to next line
        Send {Tab 8}
        Sleep 400

        ; Detect end
        clipboard := ""
        Send ^c
        ClipWait, 1

        if (clipboard = "")
            break
    }

    ; Save bill
    Send !a
    Sleep 500

    Send !y
    Sleep 800

    ; Handle linked transaction popup
    Send {Enter}
    Sleep 800
}