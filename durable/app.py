import random
import aws_durable_execution_sdk_python as durable_sdk
from aws_durable_execution_sdk_python import config as durable_sdk_config
from aws_durable_execution_sdk_python import retries as durable_sdk_retries


@durable_sdk.durable_step
def validate_payment(step_context: durable_sdk.StepContext, payment_id: str, amount: float) -> dict:
    step_context.logger.info(f"Validating payment: {payment_id} for amount: {amount}")

    if amount <= 0:
        return {"payment_id": payment_id, "status": "invalid_amount"}

    return {
        "payment_id": payment_id,
        "amount": amount,
        "status": "validated"
    }


@durable_sdk.durable_step
def request_payment_approval(step_context: durable_sdk.StepContext, callback_id: str, payment_id: str, amount: float) -> dict:
    step_context.logger.info(
        f"Sending payment {payment_id} for authorization with callback_id: {callback_id}"
    )

    return {
        "payment_id": payment_id,
        "amount": amount,
        "callback_id": callback_id,
        "status": "awaiting_authorization"
    }


@durable_sdk.durable_step
def capture_payment(step_context: durable_sdk.StepContext, payment_id: str, amount: float) -> dict:
    step_context.logger.info(f"Capturing funds for payment: {payment_id}")

    if random.random() > 0.4:
        step_context.logger.info("Gateway timeout/error, will retry")
        raise Exception("Payment gateway capture failed")

    return {
        "payment_id": payment_id,
        "amount": amount,
        "status": "captured",
        "settled_at": "2026-11-08T15:49:00Z"
    }


@durable_sdk.durable_execution
def lambda_handler(event: dict, context: durable_sdk.DurableContext) -> dict:
    payment_id: str | None = event.get("payment_id", None)

    if not payment_id:
        raise ValueError("Missing required parameter: payment_id")

    try:
        amount = event.get("amount", 0.0)

        # Paso 1: Validar el pago
        validated = context.step(validate_payment(payment_id, amount))
        if validated["status"] != "validated":
            raise Exception("Payment validation failed: Invalid payment data")
        context.logger.info(f"Payment validated: {validated}")

        # Paso 2: Crear callback para espera de aprobación bancaria / 3D Secure
        callback = context.create_callback(
            name="awaiting-payment-approval",
            config=durable_sdk_config.CallbackConfig(timeout=durable_sdk_config.Duration.from_minutes(5))
        )
        context.logger.info(f"Created callback with id: {callback.callback_id}")

        # Paso 3: Enviar la solicitud de aprobación externa con el callback_id
        approval_request = context.step(
            request_payment_approval(callback.callback_id, payment_id, amount)
        )
        context.logger.info(f"Approval request dispatched: {approval_request}")

        # Paso 4: Esperar la confirmación del banco o pasarela
        approval_result = callback.result()
        context.logger.info(f"Payment authorization result received: {approval_result}")

        # Paso 5: Capturar los fondos con reintentos exponenciales
        retry_config = durable_sdk_retries.RetryStrategyConfig(max_attempts=3, backoff_rate=2.0)
        captured = context.step(
            capture_payment(payment_id, amount),
            config=durable_sdk_config.StepConfig(retry_strategy=durable_sdk_retries.create_retry_strategy(retry_config)),
        )

        if captured["status"] != "captured":
            raise Exception("Payment capture rejected")

        context.logger.info(f"Payment successfully processed: {captured}")
        return captured

    except Exception as error:
        context.logger.error(f"Error processing payment: {error}")
        raise error
