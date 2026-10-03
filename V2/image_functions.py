from Image import (
	Image,
	scrMapImage,
	ifMapImage,
)
from Video import (
	Video,
	scrMapVideo,
	ifMapVideo,
)
from typing import Callable

def scrMap(fun: Callable,*screens: tuple) -> Image|Video:
	if isinstance(screens[0],Image):
		return scrMapImage(fun,*screens)
	if isinstance(screens[0],Video):
		return scrMapVideo(fun,*screens)
	raise ValueError
def ifMap(s1,s2,s3) -> Image|Video:
	if (
		isinstance(s1,Image) or isinstance(s2,Image) or isinstance(s3,Image)
	) and not isinstance(s1,Video) and not isinstance(s2,Video) and not isinstance(s3,Video):
		return ifMapImage(s1,s2,s3)
	if (
		isinstance(s1,Video) or isinstance(s2,Video) or isinstance(s3,Video)
	) and not isinstance(s1,Image) and not isinstance(s2,Image) and not isinstance(s3,Image):
		return ifMapVideo(s1,s2,s3)
	return ifMapImage(s1,s2,s3)