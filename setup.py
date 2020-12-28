import distutils.core

distutils.core.setup(
    name="univoucher",
    packages=["univoucher"],
    version="1.0.2",
    author="Perzan",
    author_email="PerzanDevelopment@gmail.com",
    url="https://github.com/Perzan/univoucher",
    install_requires=[
        "requests>=2.25,<3"
    ]
)
