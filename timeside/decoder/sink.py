import pygst
pygst.require('0.10')
import gst
import gobject
gobject.threads_init()

class TimesideSink(gst.BaseSink):
    """
    a simple sink element with a hopsize property to adjust the size of the buffer emitted
    """
    _caps = gst.caps_from_string('audio/x-raw-float, \
                    rate=[ 1, 2147483647 ], \
                    channels=[ 1, 2147483647 ], \
                    endianness={ 1234, 4321 }, \
                    width=32')

    __gsttemplates__ = ( 
            gst.PadTemplate ("sink",
                gst.PAD_SINK,
                gst.PAD_ALWAYS,
                _caps),
            )

    def __init__(self, name):
        self.__gobject_init__()
        self.set_name(name)
        self.adapter = gst.Adapter()
        self.set_property('sync', False)

    def set_property(self, name, value): 
        if name == 'hopsize':
            # blocksize is in byte, convert from hopsize 
            from struct import calcsize
            self.set_property('blocksize', value * calcsize('f'))
        else:
            super(gst.BaseSink, self).set_property(name, value)

    def do_render(self, buffer):
        self.adapter.push(buffer)
        return gst.FLOW_OK

    def pull(self):
        # TODO use signals
        blocksize = self.get_property('blocksize')
        remaining = self.adapter.available()
        if remaining == 0:
            return None
        if remaining >= blocksize:
            return self.adapter.take_buffer(blocksize)
        if remaining < blocksize and remaining > 0:
            return self.adapter.take_buffer(remaining)

gobject.type_register(TimesideSink)


