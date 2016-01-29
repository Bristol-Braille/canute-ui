'''
define the command codes used in communicating with the hardware
'''
CMD_GET_CHARS    = 0x00
CMD_GET_ROWS     = 0x01
CMD_SEND_DATA    = 0x02
CMD_SEND_VERSION = 0x03
CMD_SEND_ERROR   = 0x04
CMD_SEND_OK      = 0x05
CMD_SEND_ROW     = 0x06

CMD_STATUS      = 0x02
CMD_STATUS_OK   = 0x00
CMD_STATUS_ERR  = 0x01
