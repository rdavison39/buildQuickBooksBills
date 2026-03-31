CoordMode, Mouse, Screen

F2::

; --------------------------------------------------
; Click first bill to start
; --------------------------------------------------
Click 1603, 783
Sleep 500

Loop
{
    ; --------------------------------------------------
    ; Open currently selected bill
    ; --------------------------------------------------
    Send {Enter}
    Sleep 2000


    ; --------------------------------------------------
    ; Move to "Customer Job" field
    ; 13 tabs required
    ; --------------------------------------------------
    Loop 13
    {
        Send {Tab}
        Sleep 80
    }

    Sleep 500


    ; --------------------------------------------------
    ; Loop through all line items in this bill
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

        ; Move down to 20961 Skyler
        Loop 3
        {
            Send {Down}
            Sleep 80
        }

        Sleep 200

        ; Select item
        Send {Enter}
        Sleep 500

        ; Move to next line item
        Send {Tab 8}
        Sleep 400

        ; Check if next line exists
        clipboard := ""
        Send ^c
        ClipWait, 1

        ; If blank, no more line items
        if (clipboard = "")
            break
    }


    ; --------------------------------------------------
    ; Save and close bill
    ; --------------------------------------------------
    Send !a
    Sleep 500

    Send !y
    Sleep 1200


    ; --------------------------------------------------
    ; Move to next bill
    ; --------------------------------------------------
    Send {Down}
    Sleep 500


    ; --------------------------------------------------
    ; Try to open next bill
    ; If nothing opens, we are at end
    ; --------------------------------------------------
    Send {Enter}
    Sleep 1200


    ; If bill didn't open, stop script
    ; (QuickBooks window title usually changes when bill opens)
    ; If it didn't change, we're done
    ; --------------------------------------------------
    ; Move back to list and break
    IfWinNotActive, Enter Bills
    {
        break
    }


    ; We opened next bill, go back to loop start
    ; Close it so loop opens cleanly next time
    Send {Esc}
    Sleep 500
}

Return


; --------------------------------------------------
; Emergency stop
; --------------------------------------------------
Esc::ExitApp