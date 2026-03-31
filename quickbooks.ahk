CoordMode, Mouse, Screen

F2::

; --------------------------------------------------
; Row counter (which bill we are processing)
; --------------------------------------------------
row := 0

; --------------------------------------------------
; Main loop - process each bill
; --------------------------------------------------
Loop
{
    ; --------------------------------------------------
    ; Always click first row in list
    ; --------------------------------------------------
    Click 1603, 783
    Sleep 400

    ; --------------------------------------------------
    ; Move down to correct row
    ; --------------------------------------------------
    Loop %row%
    {
        Send {Down}
        Sleep 150
    }

    ; --------------------------------------------------
    ; Open selected bill
    ; --------------------------------------------------
    Send {Enter}
    Sleep 2000


    ; --------------------------------------------------
    ; Move to Customer Job dropdown (13 tabs)
    ; --------------------------------------------------
    Loop 13
    {
        Send {Tab}
        Sleep 80
    }

    Sleep 500


    ; --------------------------------------------------
    ; Loop through line items
    ; --------------------------------------------------
    Loop
    {
        ; Open dropdown
        Send !{Down}
        Sleep 400

        ; Move to top of dropdown
        Loop 6
        {
            Send {Up}
            Sleep 80
        }

        Sleep 200

        ; Move down to "20961 Skyler"
        Loop 3
        {
            Send {Down}
            Sleep 80
        }

        Sleep 200

        ; Select value
        Send {Enter}
        Sleep 500

        ; Move to next line item
        Send {Tab 8}
        Sleep 400

        ; Check if next line exists
        clipboard := ""
        Send ^c
        ClipWait, 1

        ; If blank → no more line items
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


    ; --------------------------------------------------
    ; Move to next bill
    ; --------------------------------------------------
    row++
}

Return


; --------------------------------------------------
; Emergency stop
; --------------------------------------------------
Esc::ExitApp