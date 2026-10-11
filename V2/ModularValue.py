from Interval import Interval

class ModularValue:
	def __init__(self,*args) -> None:
		match len(args):
			case 1:
				if not isinstance(args[0],ModularValue):
					raise TypeError(f"ModularValue({args[0]})")
				self.value = args[0].values
				self.modulus = args[0].modulus
			case 2:
				self.value = args[0]
				self.modulus = args[1]
				if not isinstance(self.value,int|float) or not isinstance(self.modulus,int|float):
					raise TypeError(f"ModularValue{args}")
			case _:
				raise TypeError(f"ModularValue{args}")
		self.value %= self.modulus
	def __add__(self,value: int|float|ModularValue) -> ModularValue:
		if isinstance(value,ModularValue): return self + value.value
		if isinstance(value,int|float): return ModularValue(self.value + value,self.modulus)
		return NotImplemented
	def __sub__(self,value: int|float|ModularValue) -> ModularValue:
		if isinstance(value,ModularValue): return self - value.value
		if isinstance(value,int|float): return ModularValue(self.value - value,self.modulus)
		return NotImplemented
	def __mul__(self,value: int|float|ModularValue) -> ModularValue:
		if isinstance(value,ModularValue): return self * value.value
		if isinstance(value,int|float): return ModularValue(self.value * value,self.modulus)
		return NotImplemented
	def __truediv__(self,value: int|float|ModularValue) -> ModularValue:
		if isinstance(value,ModularValue): return self / value.value
		if isinstance(value,int|float): return ModularValue(self.value / value,self.modulus)
		return NotImplemented
	def __floordiv__(self,value: int|float|ModularValue) -> ModularValue:
		if isinstance(value,ModularValue): return self // value.value
		if isinstance(value,int|float): return ModularValue(self.value // value,self.modulus)
		return NotImplemented
	def __mod__(self,value: int|float|ModularValue) -> ModularValue:
		if isinstance(value,ModularValue): return self % value.value
		if isinstance(value,int|float): return ModularValue(self.value % value,self.modulus)
		return NotImplemented