# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.2
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.





from sys import version_info
if version_info >= (2,6,0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_EST_Wave', [dirname(__file__)])
        except ImportError:
            import _EST_Wave
            return _EST_Wave
        if fp is not None:
            try:
                _mod = imp.load_module('_EST_Wave', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _EST_Wave = swig_import_helper()
    del swig_import_helper
else:
    import _EST_Wave
del version_info
try:
    _swig_property = property
except NameError:
    pass # Python < 2.2 doesn't have 'property'.
def _swig_setattr_nondynamic(self,class_type,name,value,static=1):
    if (name == "thisown"): return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'SwigPyObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    if (not static):
        self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)

def _swig_setattr(self,class_type,name,value):
    return _swig_setattr_nondynamic(self,class_type,name,value,0)

def _swig_getattr(self,class_type,name):
    if (name == "thisown"): return self.this.own()
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError(name)

def _swig_repr(self):
    try: strthis = "proxy of " + self.this.__repr__()
    except: strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

try:
    _object = object
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0


read_ok = _EST_Wave.read_ok
read_format_error = _EST_Wave.read_format_error
read_not_found_error = _EST_Wave.read_not_found_error
read_error = _EST_Wave.read_error
write_ok = _EST_Wave.write_ok
write_fail = _EST_Wave.write_fail
write_error = _EST_Wave.write_error
write_partial = _EST_Wave.write_partial
connect_ok = _EST_Wave.connect_ok
connect_not_found_error = _EST_Wave.connect_not_found_error
connect_not_allowed_error = _EST_Wave.connect_not_allowed_error
connect_system_error = _EST_Wave.connect_system_error
connect_error = _EST_Wave.connect_error
class EST_Wave(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, EST_Wave, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, EST_Wave, name)
    __repr__ = _swig_repr
    __swig_getmethods__["default_sample_rate"] = _EST_Wave.EST_Wave_default_sample_rate_get
    if _newclass:default_sample_rate = _swig_property(_EST_Wave.EST_Wave_default_sample_rate_get)
    def __init__(self, *args): 
        this = _EST_Wave.new_EST_Wave(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _EST_Wave.delete_EST_Wave
    __del__ = lambda self : None;
    def a(self, *args): return _EST_Wave.EST_Wave_a(self, *args)
    def a_safe(self, *args): return _EST_Wave.EST_Wave_a_safe(self, *args)
    def set_a(self, *args): return _EST_Wave.EST_Wave_set_a(self, *args)
    def t(self, *args): return _EST_Wave.EST_Wave_t(self, *args)
    def num_samples(self): return _EST_Wave.EST_Wave_num_samples(self)
    def num_channels(self): return _EST_Wave.EST_Wave_num_channels(self)
    def sample_rate(self): return _EST_Wave.EST_Wave_sample_rate(self)
    def set_sample_rate(self, *args): return _EST_Wave.EST_Wave_set_sample_rate(self, *args)
    def length(self): return _EST_Wave.EST_Wave_length(self)
    def end(self): return _EST_Wave.EST_Wave_end(self)
    def have_left_context(self, *args): return _EST_Wave.EST_Wave_have_left_context(self, *args)
    def sample_type(self): return _EST_Wave.EST_Wave_sample_type(self)
    def set_sample_type(self, *args): return _EST_Wave.EST_Wave_set_sample_type(self, *args)
    def file_type(self): return _EST_Wave.EST_Wave_file_type(self)
    def set_file_type(self, *args): return _EST_Wave.EST_Wave_set_file_type(self, *args)
    def name(self): return _EST_Wave.EST_Wave_name(self)
    def set_name(self, *args): return _EST_Wave.EST_Wave_set_name(self, *args)
    def resize(self, *args): return _EST_Wave.EST_Wave_resize(self, *args)
    def resample(self, *args): return _EST_Wave.EST_Wave_resample(self, *args)
    def rescale(self, *args): return _EST_Wave.EST_Wave_rescale(self, *args)
    def clear(self): return _EST_Wave.EST_Wave_clear(self)
    def copy(self, *args): return _EST_Wave.EST_Wave_copy(self, *args)
    def fill(self, *args): return _EST_Wave.EST_Wave_fill(self, *args)
    def empty(self, *args): return _EST_Wave.EST_Wave_empty(self, *args)
    def load(self, *args): return _EST_Wave.EST_Wave_load(self, *args)
    def load_file(self, *args): return _EST_Wave.EST_Wave_load_file(self, *args)
    def save(self, *args): return _EST_Wave.EST_Wave_save(self, *args)
    def save_file(self, *args): return _EST_Wave.EST_Wave_save_file(self, *args)
    def integrity(self): return _EST_Wave.EST_Wave_integrity(self)
    def info(self): return _EST_Wave.EST_Wave_info(self)
    def play(self): return _EST_Wave.EST_Wave_play(self)
EST_Wave_swigregister = _EST_Wave.EST_Wave_swigregister
EST_Wave_swigregister(EST_Wave)


def wave_extract_channel(*args):
  return _EST_Wave.wave_extract_channel(*args)
wave_extract_channel = _EST_Wave.wave_extract_channel

def wave_combine_channels(*args):
  return _EST_Wave.wave_combine_channels(*args)
wave_combine_channels = _EST_Wave.wave_combine_channels

def wave_subwave(*args):
  return _EST_Wave.wave_subwave(*args)
wave_subwave = _EST_Wave.wave_subwave

def wave_divide(*args):
  return _EST_Wave.wave_divide(*args)
wave_divide = _EST_Wave.wave_divide

def wave_extract(*args):
  return _EST_Wave.wave_extract(*args)
wave_extract = _EST_Wave.wave_extract

def add_waves(*args):
  return _EST_Wave.add_waves(*args)
add_waves = _EST_Wave.add_waves

def difference(*args):
  return _EST_Wave.difference(*args)
difference = _EST_Wave.difference

def rms_error(*args):
  return _EST_Wave.rms_error(*args)
rms_error = _EST_Wave.rms_error

def abs_error(*args):
  return _EST_Wave.abs_error(*args)
abs_error = _EST_Wave.abs_error

def correlation(*args):
  return _EST_Wave.correlation(*args)
correlation = _EST_Wave.correlation

def error(*args):
  return _EST_Wave.error(*args)
error = _EST_Wave.error

def absolute(*args):
  return _EST_Wave.absolute(*args)
absolute = _EST_Wave.absolute

def wave_info(*args):
  return _EST_Wave.wave_info(*args)
wave_info = _EST_Wave.wave_info

def invert(*args):
  return _EST_Wave.invert(*args)
invert = _EST_Wave.invert

def differentiate(*args):
  return _EST_Wave.differentiate(*args)
differentiate = _EST_Wave.differentiate

def reverse(*args):
  return _EST_Wave.reverse(*args)
reverse = _EST_Wave.reverse
# This file is compatible with both classic and new-style classes.


