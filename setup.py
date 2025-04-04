from setuptools import find_packages, setup

package_name = 'ros_api_comm'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ubuntu',
    maintainer_email='ubuntu@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        # executable_name = pkg_name.file_name:func_name 
        'console_scripts': [
            "RosApiBridge = ros_api_comm.RosApiBridge:main"
        ],
    },
)
