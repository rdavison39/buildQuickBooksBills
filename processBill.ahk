; ==================================================
; ProcessBill.ahk
; ==================================================

ProcessBill()
{
    ; --------------------------------------------------
    ; Move to Customer Job dropdown
    ; --------------------------------------------------
    Click 1497, 726 
    Loop 2
    {
        Send {Tab}
        Sleep 80
    }

    Sleep 500


    ; --------------------------------------------------
    ; Loop through all line items
    ; --------------------------------------------------
    Loop
    {
        found := false

        ; --------------------------------------------------
        ; Open dropdown
        ; --------------------------------------------------
        Send !{Down}
        Sleep 400

        ; --------------------------------------------------
        ; Move to top
        ; --------------------------------------------------
        Loop 6
        {
            Send {Up}
            Sleep 80
        }

        ; --------------------------------------------------
        ; Scan dropdown items
        ; --------------------------------------------------
        Loop 6
        {
            ; Select current item
            Send {Enter}
            Sleep 300

            ; Copy selected value
            clipboard := ""
            Send ^c
            ClipWait, .3

            ; Check if correct job
            if InStr(clipboard, "20961 Skyler")
            {
                found := true
                break
            }

            ; Reopen dropdown
            Send !{Down}
            Sleep 200

            ; Move down to next item
            Send {Down}
            Sleep 150
        }

        ; --------------------------------------------------
        ; Move to next line item
        ; --------------------------------------------------
        Send {Tab 8}
        Sleep 400


        ; --------------------------------------------------
        ; Check if next line exists
        ; --------------------------------------------------
        clipboard := ""
        Send ^c
        ClipWait, 1

        if (clipboard = "")
            break
    }


    ; --------------------------------------------------
    ; Save bill
    ; --------------------------------------------------
    Send !a
    Sleep 500

    Send !y
    Sleep 1200
}