import esphome.codegen as cg
from esphome.components import uart
import esphome.config_validation as cv
from esphome.const import CONF_ADDRESS, CONF_FLOW_CONTROL_PIN, CONF_ID
from esphome.cpp_helpers import gpio_pin_expression
from esphome import pins

CODEOWNERS = ["@syssi"]
DEPENDENCIES = ["uart"]

modbus_solax_ns = cg.esphome_ns.namespace("modbus_solax")
ModbusSolax = modbus_solax_ns.class_("ModbusSolax", cg.Component, uart.UARTDevice)
ModbusSolaxDevice = modbus_solax_ns.class_("ModbusSolaxDevice")
MULTI_CONF = True

CONF_MODBUS_SOLAX_ID = "modbus_solax_id"
CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(ModbusSolax),
            cv.Optional(CONF_FLOW_CONTROL_PIN): pins.gpio_output_pin_schema,
        }
    )
    .extend(cv.COMPONENT_SCHEMA)
    .extend(uart.UART_DEVICE_SCHEMA)
)


def as_hex_array(value):
    cpp_array = [
        f"0x{part}" for part in [value[i : i + 2] for i in range(0, len(value), 2)]
    ]
    return cg.RawExpression(f"(uint8_t*)(const uint8_t[16]){{{','.join(cpp_array)}}}")


async def to_code(config):
    cg.add_global(modbus_solax_ns.using)
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    await uart.register_uart_device(var, config)

    if CONF_FLOW_CONTROL_PIN in config:
        pin = await gpio_pin_expression(config[CONF_FLOW_CONTROL_PIN])
        cg.add(var.set_flow_control_pin(pin))


def modbus_solax_device_schema():
    schema = {
        cv.GenerateID(CONF_MODBUS_SOLAX_ID): cv.use_id(ModbusSolax),
        cv.Required(CONF_ADDRESS): cv.hex_uint8_t,
    }
    return cv.Schema(schema)


async def register_modbus_solax_device(var, config):
    parent = await cg.get_variable(config[CONF_MODBUS_SOLAX_ID])
    cg.add(var.set_parent(parent))
    cg.add(var.set_address(config[CONF_ADDRESS]))
    cg.add(parent.register_device(var))
