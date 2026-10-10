class NoiseBlock:
	def __init__(self,dimensions: int,size: int,seed: int,scale: int,frequency: int|float,time: int|float) -> None:
		self.dimensions = dimensions
		self.size = size
		self.seed = seed
		self.scale = scale
		self.frequency = frequency
		self.time = time
	def __iter__(self) -> iter:
		yield self.dimensions
		yield self.size
		yield self.seed
		yield self.scale
		yield self.frequency
		yield self.time
	def __hash__(self) -> int:
		return hash(tuple(self))
	def __eq__(self,value) -> bool:
		return isinstance(value,NoiseBlock) and hash(self) == hash(value)
	def __ne__(self,value) -> bool:
		return not (self == value)
	def __str__(self) -> str:
		return f"NoiseBlock{tuple(self)}"
	def __repr__(self) -> str:
		return str(self)