from datetime import UTC, datetime
import json
import random

import aws_durable_execution_sdk_python as durable_sdk
from aws_durable_execution_sdk_python import (
    config as durable_sdk_config,
    retries as durable_sdk_retries,
)


@durable_sdk.durable_step
def validate_payment(
    step_context: durable_sdk.StepContext, payment_id: str, amount: float
) -> dict:
    step_context.logger.info(
        f"[PASO 1] Validando pago {payment_id} por monto ${amount}"
    )

    if amount <= 0:
        return {"payment_id": payment_id, "status": "invalid_amount"}

    return {"payment_id": payment_id, "amount": amount, "status": "validated"}


@durable_sdk.durable_step
def request_payment_approval(
    step_context: durable_sdk.StepContext,
    callback_id: str,
    payment_id: str,
    amount: float,
) -> dict:
    step_context.logger.info(
        f"[PASO 2] Notificando aprobación para pago {payment_id} por monto ${amount}"
    )

    return {
        "payment_id": payment_id,
        "amount": amount,
        "callback_id": callback_id,
        "status": "awaiting_authorization",
    }


@durable_sdk.durable_step
def capture_payment(
    step_context: durable_sdk.StepContext,
    payment_id: str,
    amount: float,
    approved_by: str,
) -> dict:
    step_context.logger.info(
        f"[PASO 4] Intentando capturar fondos para {payment_id} (Aprobado por: {approved_by})"
    )

    if random.random() > 0.4:
        step_context.logger.warning(
            "Fallo temporal en pasarela de pagos (Timeout). Reintentando..."
        )
        raise Exception("Payment gateway capture failed")

    return {
        "payment_id": payment_id,
        "amount": amount,
        "approved_by": approved_by,
        "status": "captured",
        "settled_at": datetime.now(UTC).isoformat(),
    }


@durable_sdk.durable_execution
def lambda_handler(event: dict, context: durable_sdk.DurableContext) -> dict:
    payment_id: str | None = event.get("payment_id")
    amount: float | None = event.get("amount")

    if not payment_id or amount is None:
        raise ValueError("Faltan parámetros requeridos: 'payment_id' y 'amount'")

    try:
        # Paso 1: Validar el pago (Checkpoint 1)
        validated = context.step(validate_payment(payment_id, amount))
        if validated["status"] != "validated":
            raise ValueError(
                f"Validación fallida para pago {payment_id}: monto inválido"
            )

        # Paso 2: Crear el token de Callback (Checkpoint 2)
        callback = context.create_callback(
            name="awaiting-payment-approval",
            config=durable_sdk_config.CallbackConfig(
                timeout=durable_sdk_config.Duration.from_minutes(5)
            ),
        )
        context.step(request_payment_approval(callback.callback_id, payment_id, amount))

        # Paso 3: Pausar ejecución hasta recibir respuesta externa (Checkpoint 4)
        raw_approval = callback.result()
        approval_data = (
            json.loads(raw_approval)
            if isinstance(raw_approval, str)
            else (raw_approval or {})
        )
        context.logger.info(
            f"[PASO 3] Respuesta de aprobación recibida: {approval_data}"
        )

        if not approval_data.get("approved", False):
            return {
                "payment_id": payment_id,
                "status": "rejected_by_approver",
                "reason": approval_data.get("reason", "No especificado"),
            }

        approved_by = approval_data.get("approver", "admin_manual")

        # Paso 4: Capturar fondos con estrategia de reintentos exponenciales (Checkpoint 5)
        retry_config = durable_sdk_retries.RetryStrategyConfig(
            max_attempts=4,
            initial_delay=durable_sdk_config.Duration.from_seconds(2),
            backoff_rate=2.0,
        )
        captured = context.step(
            capture_payment(payment_id, amount, approved_by),
            config=durable_sdk_config.StepConfig(
                retry_strategy=durable_sdk_retries.create_retry_strategy(retry_config)
            ),
        )

        context.logger.info(f"[FIN] Pago completado exitosamente: {captured}")
        return captured

    except Exception as error:
        context.logger.error(
            f"[ERROR] Fallo en el flujo del pago {payment_id}: {error}"
        )
        raise
