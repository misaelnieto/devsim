DEVSIM_CONFIG="centos_6"
CMAKE="/usr/bin/cmake3"
CMAKE_CXX_FLAGS=""
CXX="/opt/rh/devtoolset-6/root/usr/bin/g++"
CC="/opt/rh/devtoolset-6/root/usr/bin/gcc"
for TYPE in debug release; do
ARCH=`uname -m`
#  for ARCH in i386 x86_64; do
    NAME=linux_${ARCH}_${TYPE}
    mkdir ${NAME}
    (cd $NAME; ${CMAKE} \
      -DCMAKE_BUILD_TYPE=${TYPE} \
      -DCMAKE_CXX_COMPILER=${CXX} \
      -DCMAKE_C_COMPILER=${CC} \
      -DDEVSIM_CONFIG=${DEVSIM_CONFIG} \
      -DCMAKE_CXX_FLAGS:STRING="${CMAKE_CXX_FLAGS}" \
      -DDEVSIM_EXTENDED_PRECISION=ON \
      -DMKL_PARDISO=ON \
      -DPYTHON3=ON \
      ..)
#  done
done
