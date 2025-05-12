    MOV     R2, #0
    CMP     R5, R2      ; compare k and 0
    JNZA    kNot0
    STP                 ; if k = 0, we stop
kNot0:
    MOV     R1, #0      ; initialize loop counter
    MOV     R2, #1      ; set to 1 to increment loop counter
loop:
    POW     R6, R6      ; perform the modular square
    ADD     R1, R1, R2  ; update loop counter
    CMP     R1, R5      ; compare with k
    JNZA    loop        ; loop again if we are not done
    STP                 ; an error is raised if we don't explicitly stop
