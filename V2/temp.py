import matplotlib.pyplot as plt
import numpy as np
from math import (
	cos,
	sin,
	tau,
)

def getCurrentTilt(day: int,tilt: int|float) -> float:
	return -tilt + day * 2 * tilt/365
def lattitudeToAngle(latt: int,size: int) -> float:
	return latt * tau/size
def getAngleForDay(latt: int,day: int,size: int,tilt: int|float) -> float:
	return (
		lattitudeToAngle(latt,size) + getCurrentTilt(day,tilt)
	) % tau
def getVectorForDay(latt: int,day: int,size: int,tilt: int|float) -> tuple[float,float]:
	theta = getAngleForDay(latt,day,size,tilt)
	return (
		(size/tau) * cos(theta),
		(size/tau) * sin(theta),
	)
def getSunlightValue(lattitude: int,day: int,size: int,tilt: int|float) -> float:
	x,y = getVectorForDay(lattitude,day,size,tilt)
	return x * -size/tau
def getNormalizedSunlightValue(lattitude: int,day: int,size: int,tilt: int|float) -> float:
	return (
		getSunlightValue(lattitude,day,size,tilt) + getSunlightValue(size - lattitude,day,size,tilt)
	)/2
def getAvgSunlightValue(lattitude: int,sunlightMax: int|float,sunlightMin: int|float,size: int,tilt: int|float) -> float:
	values = [getNormalizedSunlightValue(lattitude,day,size,tilt) for day in range(365)]
	return (
		sum(values)/len(values) + (size/tau)**2
	) * (
		sunlightMax - sunlightMin
	) / (
		2 * (size/tau)**2
	) + sunlightMin
SUNLIGHT_MAX = 255
SUNLIGHT_MIN = 0
SIZE = 256
TILT = 23.44 * tau/360

a = [i for i in range(SIZE)]
b = [
	getAvgSunlightValue(
		lattitude = y,
		sunlightMax = SUNLIGHT_MAX,
		sunlightMin = SUNLIGHT_MIN,
		size = SIZE,
		tilt = TILT,
	) for y in range(SIZE)
]
print(b[127])
plt.plot(a,b)
plt.show()
