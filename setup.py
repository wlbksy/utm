from setuptools import find_packages, setup

setup(
    name="utm",
    version="0.1",
    description="convert between WGS84 and UTM",
    author="WANG Lei",
    author_email="wlbksy@126.com",
    license="MIT",
    packages=find_packages(),
    platforms=["Windows", "Linux", "Mac OS-X"],
    python_requires=">=3.7",
    classifiers=["Programming Language :: Python :: 3 :: Only",],
    zip_safe=False,
)
