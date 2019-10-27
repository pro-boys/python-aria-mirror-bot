FROM 3.7.4-alpine3.10

RUN apk add --no-cache --update \
      git \
      aria2

RUN mkdir /bot
RUN chmod 777 /bot
COPY . /bot
WORKDIR /bot

CMD ["python","-m","bot"]
