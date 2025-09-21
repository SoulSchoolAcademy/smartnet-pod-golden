# REPO: SoulSchoolAcademy/smartnet-pod-golden
# PATH: /Dockerfile (repo root)
FROM alpine:3.20
WORKDIR /app
RUN adduser -D app && chown -R app:app /app
USER app
# Copying repo isn't required for this smoke, but harmless and proves copy works
COPY --chown=app:app . /app
# Simple long-running container to prove publish works
CMD ["sh","-c","echo 'smartnet-pod-golden online ✅'; tail -f /dev/null"]
