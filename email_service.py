# =========================================================
# EMAIL DI CONFERMA AL CLIENTE
# =========================================================

if email.strip():

    try:

        send_booking_confirmation(
            recipient_email=email.strip(),
            nome_farmacia=nome_farmacia.strip(),
            cap=cap.strip(),
            start_datetime=selected_slot["start"],
            end_datetime=selected_slot["end"],
            durata=durata,
            referente=referente.strip(),
        )

    except Exception as e:

        print(
            "Errore invio email conferma:",
            e,
        )
