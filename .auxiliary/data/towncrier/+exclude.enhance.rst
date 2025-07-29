Add ``exclude`` decorator to prevent other Dynadoc processing of the object.
Does not actually decorate the object in any way, but adds it to Dynadoc's
visitees registry, which will cause the Dyandoc decorators to short-circuit on
the object.
