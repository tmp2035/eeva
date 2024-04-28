
FROM python:3.11-bookworm

LABEL version="0.0.3"

WORKDIR /

# install dependency
RUN apt update && apt-get install -yqq libglib2.0-dev libgoogle-perftools-dev cmake git sudo wget gcc g++ xxhash
# RUN apt update && apt-get install -yqq cmake git sudo wget gcc g++ xxhash libglib2.0-dev

# clone repos
RUN git clone https://github.com/1a1a11a/libCacheSim -b develop
RUN git clone https://github.com/tmp2035/cache.git


# build cache
WORKDIR /cache/
RUN pip install -e . --force-reinstall

# build libCacheSim
WORKDIR /libCacheSim/
RUN git reset --hard 3080f2c2643b7a2b03bcfb7c5837f6fff3aa8908

# our changed file
RUN rm /libCacheSim/libCacheSim/bin/cachesim/sim.c
RUN cp /cache/libcache/sim.c /libCacheSim/libCacheSim/bin/cachesim/sim.c

RUN mkdir _build;
RUN bash ./scripts/install_dependency.sh
RUN bash ./scripts/install_libcachesim.sh


WORKDIR /libCacheSim/_build/
RUN cmake -DSUPPORT_ZSTD_TRACE=on .. && make -j && sudo make install

WORKDIR /
RUN mkdir runs
# WORKDIR /libCacheSim/_build/bin/
CMD bash
