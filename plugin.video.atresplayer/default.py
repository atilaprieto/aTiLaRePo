import sys
import base64
exec(base64.b64decode('aW1wb3J0IHhibWNndWkseGJtY3BsdWdpbix4Ym1jLHVybGxpYix1cmxsaWIyLHVybHBhcnNlLGpzb24seGJtY2FkZG9uLG9zLHJlLHJhbmRvbSxyZXF1ZXN0cyx1bmljb2RlZGF0YSx1cmxyZXNvbHZlcixyZXNvbHZldXJsCmZyb20gc3FsaXRlMyBpbXBvcnQgZGJhcGkyIGFzIGRhdGFiYXNlCmZyb20gdHlwZXMgaW1wb3J0IFVuaWNvZGVUeXBlCmZyb20gRjRtUHJveHkgaW1wb3J0IGY0bVByb3h5SGVscGVyCmZyb20gcmVzb2x2ZXVybC5wbHVnaW5zLmxpYiBpbXBvcnQganN1bnBhY2sKTzAwMHhPTzAwMDAwMDAwPXN5cy5hcmd2WzBdCk8wMDB4MDAwT09PT09PTz1pbnQoc3lzLmFyZ3ZbMV0pCk9PMDB4MDAwMDAwMDBPMD11cmxwYXJzZS5wYXJzZV9xcyhzeXMuYXJndlsyXVsxOl0pCk8wMDB4ME9PT09PT09PTz14Ym1jYWRkb24uQWRkb24oKQpPMDAweDBPT09PT09PTzA9TzAwMHgwT09PT09PT09PLmdldEFkZG9uSW5mbygncGF0aCcpCnN5cy5wYXRoLmFwcGVuZCh4Ym1jLnRyYW5zbGF0ZVBhdGgob3MucGF0aC5qb2luKE8wMDB4ME9PT09PT09PMCwnbGliJykpKQpPMDAweDAwMDAwMDBPT089b3MucGF0aC5qb2luKHhibWMudHJhbnNsYXRlUGF0aCgic3BlY2lhbDovL2RhdGFiYXNlIiksJ2F0cmVzcGxheWVyLmRiJykKTzAwMHgwMDAwMDBPTzAwPWRhdGFiYXNlLmNvbm5lY3QoTzAwMHgwMDAwMDAwT09PKQpPMDAweDAwMDAwMDBPTzA9TzAwMHgwMDAwMDBPTzAwLmN1cnNvcigpCmRlZiBPMDAwMHgwMDAwMDAwMDAoTzAwMDB4MDAwMDAwMDBPKToKICAgIE8wMDAweDAwMDAwMDBPMD1bXQogICAgTzAwMDB4MDBPMDAwMDAwPU8wMDAweDAwMDAwMDAwTy5zcGxpdCgnXycpCiAgICBPMDAwMHgwTzAwMDAwMDA9TzAwMDB4MDBPMDAwMDAwWzFdLnNwbGl0KCcvJykKICAgIE8wMDAweDAwME9PMDAwMD1vcGVuKE8wMDB4ME9PT09PT09PMCsnL3Jlc291cmNlcy9zZXR0aW5ncy50eHQnLCJyIikKICAgIE8wMDAweDAwMDBPMDAwMD1iYXNlNjQuYjY0ZGVjb2RlKE8wMDAweDAwME9PMDAwMC5yZWFkKCkpCiAgICBPMDAwMHgwMDBPTzAwMDAuY2xvc2UoKQogICAgTzAwMDB4MDAwMDAwTzAwPU8wMDAweDAwMDBPMDAwMAogICAgTzAwMDB4MDAwMDAwME9PPU8wMDAweDAwMDAwME8wMC5zcGxpdCgiXG4iKQogICAgZm9yIE8wMDAweDAwME8wMDAwMCBpbiByYW5nZSgwLGxlbihPMDAwMHgwMDAwMDAwT08pKToKICAgICAgICBpZiBPMDAwMHgwTzAwMDAwMDBbMF0gaW4gTzAwMDB4MDAwMDAwME9PW08wMDAweDAwME8wMDAwMF06CiAgICAgICAgICAgIE8wMDAweE8wMDAwMDAwMD1PMDAwMHgwMDAwMDAwT09bTzAwMDB4MDAwTzAwMDAwXS5zcGxpdChPMDAwMHgwTzAwMDAwMDBbMF0rJzonKQogICAgICAgICAgICBPMDAwMHgwMDAwMDAwTzAuYXBwZW5kKHsnTzAwMDB4MDAwMDAwT08wJzpPMDAwMHhPMDAwMDAwMDBbMV19KQogICAgcmV0dXJuIE8wMDAweDAwMDAwMDBPMApkZWYgTzAwMHgwMDAwMDAwMDAwKE8wMDB4MDAwMDBPTzAwMCk6CiAgICB0cnk6CiAgICAgICAgTzAwMHgwMDAwME9PMDAwPXVuaWNvZGUoTzAwMHgwMDAwME9PMDAwLmVuY29kZSgidXRmLTgiKSwndXRmLTgnKQogICAgZXhjZXB0IE5hbWVFcnJvcjoKICAgICAgICBwYXNzCiAgICBPMDAweDAwMDAwT08wMDA9dW5pY29kZWRhdGEubm9ybWFsaXplKCdORkQnLE8wMDB4MDAwMDBPTzAwMClcCiAgICAgICAgICAgLmVuY29kZSgnYXNjaWknLCdpZ25vcmUnKVwKICAgICAgICAgICAuZGVjb2RlKCJ1dGYtOCIpCiAgICByZXR1cm4gc3RyKE8wMDB4MDAwMDBPTzAwMCkKZGVmIE8wMDB4MDAwMDAwTzAwMChPMDAweDAwMDAwMDAwME8pOgogICAgTzAwMHgwMDAwMDAwTzAwPU8wMDB4MDAwMDAwMDAwMChPMDAweDAwMDAwMDAwME8pCiAgICBPMDAweDAwMDAwMDBPMDA9cmUuc3ViKHInWyNcXC86Iio/PD58XSsnLCIiLE8wMDB4MDAwMDAwME8wMCkKICAgIE8wMDB4MDAwMDAwME8wMD0iIi5qb2luKGkgZm9yIGkgaW4gTzAwMHgwMDAwMDAwTzAwIGlmIG9yZChpKTwxMjgpCiAgICBPMDAweDAwMDAwMDBPMDA9JyAnLmpvaW4oTzAwMHgwMDAwMDAwTzAwLnNwbGl0KCkpCiAgICByZXR1cm4gTzAwMHgwMDAwMDAwTzAwCmRlZiBPMDAweDAwMDAwME9PTzAoTzAwMHgwMDAwMDAwMDBPKToKICAgIHJldHVybiBPMDAweDAwMDAwMDAwTzAoTzAwMHgwMDAwMDAwMDBPKS5lbmNvZGUoJ3V0Zi04JykKZGVmIE8wMDB4MDAwMDAwMDBPMChPMDAweDAwMDAwTzAwMDApOgogICAgaWYgdHlwZShPMDAweDAwMDAwTzAwMDApIGlzIFVuaWNvZGVUeXBlOgogICAgICAgIHJldHVybiBPMDAweDAwMDAwTzAwMDAKICAgIGVsc2U6CiAgICAgICAgdHJ5OgogICAgICAgICAgICByZXR1cm4gdW5pY29kZShPMDAweDAwMDAwTzAwMDAsJ3V0Zi04JykKICAgICAgICBleGNlcHQ6CiAgICAgICAgICAgIHJldHVybiB1bmljb2RlKE8wMDB4MDAwMDBPMDAwMCwnaXNvLTg4NTktMScpCmRlZiBPMDAweDBPTzAwMDAwMDAoTzAwMHgwMDAwME9PTzAwKToKICAgIHJldHVybiBPMDAweE9PMDAwMDAwMDArJz8nK3VybGxpYi51cmxlbmNvZGUoTzAwMHgwMDAwME9PTzAwKQpkZWYgTzAwMHgwT09PT08wMDAwKE8wMDB4MDAwTzAwMDAwMCxPMDAweDAwMDBPMDAwMDApOgogICAgTzAwMHgwME8wMDAwMDAwPVtdCiAgICBpZiBPMDAweDAwMDBPMDAwMDA9PTM6CiAgICAgICAgcmV0dXJuIE8wMDB4MDBPMDAwMDAwMAogICAgZWxzZToKICAgICAgICBPMDAweDAwME8wMDAwMDA9TzAwMHgwMDBPMDAwMDAwLnJlcGxhY2UoJyAnLCclMjAnKQogICAgICAgIE8wMDB4MDAwMDAwME9PMC5leGVjdXRlKCJDUkVBVEUgVEFCTEUgSUYgTk9UIEVYSVNUUyBhM2xpbmtzIChwYWdlX2xpbmsgVEVYVCwgcmV0dXJuX2xpbmsgVEVYVCwgdGlwbyBURVhULCBVTklRVUUocGFnZV9saW5rLCB0aXBvKSk7IikKICAgICAgICBPMDAweDAwMDAwME9PMDAuY29tbWl0KCkKICAgICAgICBPMDAweDAwMDAwMDBPTzAuZXhlY3V0ZSgiU0VMRUNUIHJldHVybl9saW5rLCB0aXBvIEZST00gYTNsaW5rcyBXSEVSRSBwYWdlX2xpbmsgPSAnIitPMDAweDAwME8wMDAwMDArIiciKQogICAgICAgIE8wMDB4MDAwME9PMDAwMD1PMDAweDAwMDAwMDBPTzAuZmV0Y2hhbGwoKQogICAgICAgIGlmIGxlbihPMDAweDAwMDBPTzAwMDApPjA6CiAgICAgICAgICAgIGZvciBPMDAweDAwME9PMDAwMDAgaW4gTzAwMHgwMDAwT08wMDAwOgogICAgICAgICAgICAgICAgTzAwMHgwME8wMDAwMDAwLmFwcGVuZCh7J08wMDB4MDBPTzAwMDAwMCc6TzAwMHgwMDBPTzAwMDAwWzBdLCdPMDAweDAwMDAwMDAwT08nOk8wMDB4MDAwT08wMDAwMFsxXX0pCiAgICAgICAgICAgIHJldHVybiBPMDAweDAwTzAwMDAwMDAKICAgICAgICBlbHNlOgogICAgICAgIAl0cnk6CiAgICAgICAgCQlPMDAweDAwMDBPT09PTzA9eydTZWMtRmV0Y2gtTW9kZSc6J2NvcnMnLCdPcmlnaW4nOidodHRwczovL2VsamF2aWVyby5jb20nLCdBY2NlcHQtTGFuZ3VhZ2UnOidlcy1FUyxlcztxPTAuOScsJ1gtUmVxdWVzdGVkLVdpdGgnOidYTUxIdHRwUmVxdWVzdCcsJ0Nvbm5lY3Rpb24nOidrZWVwLWFsaXZlJywnUHJhZ21hJzonbm8tY2FjaGUnLCdVc2VyLUFnZW50JzonTW96aWxsYS81LjAgKFgxMTsgTGludXggeDg2XzY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvNzcuMC4zODY1LjEyMCBTYWZhcmkvNTM3LjM2JywnQ29udGVudC1UeXBlJzonYXBwbGljYXRpb24veC13d3ctZm9ybS11cmxlbmNvZGVkOyBjaGFyc2V0PVVURi04JywnQWNjZXB0JzonKi8qJywnQ2FjaGUtQ29udHJvbCc6J25vLWNhY2hlJywnUmVmZXJlcic6J2h0dHBzOi8vZWxqYXZpZXJvLmNvbS9kZXNjYXJnYXJ2aWRlb3NkZWxhdGVsZS9kb3dubG9hZC8nLCdTZWMtRmV0Y2gtU2l0ZSc6J3NhbWUtb3JpZ2luJ30KICAgICAgICAJCU8wMDB4MDBPT09PTzAwMD11cmxsaWIudXJsZW5jb2RlKHsndXJsX25vdGljaWEnOk8wMDB4MDAwTzAwMDAwMCwnc3VibWl0X2Vudmlhcl91cmwnOidvaycsJ2N1cnJlbnRfdXJsJzonaHR0cHM6Ly9lbGphdmllcm8uY29tL2Rlc2NhcmdhcnZpZGVvc2RlbGF0ZWxlL2Rvd25sb2FkLyd9KQogICAgICAgIAkJTzAwMHgwMDBPT09PMDAwPXVybGxpYjIuUmVxdWVzdCgiaHR0cHM6Ly9lbGphdmllcm8uY29tL2Rlc2NhcmdhcnZpZGVvc2RlbGF0ZWxlL2luZGV4LnBocCIsZGF0YT1PMDAweDAwT09PT08wMDAsaGVhZGVycz1PMDAweDAwMDBPT09PTzApCiAgICAgICAgCQlPMDAweDAwMDBPT08wMDA9anNvbi5sb2Fkcyh1cmxsaWIyLnVybG9wZW4oTzAwMHgwMDBPT09PMDAwKS5yZWFkKCkpCiAgICAgICAgCQlpZiAncHJ1ZWJhIGRlIG51ZXZvJyBpbiBPMDAweDAwMDBPT08wMDBbJ21lbnNhamUnXToKICAgICAgICAJCQlPMDAweDAwMDBPMDAwMDA9TzAwMHgwMDAwTzAwMDAwKzEKICAgICAgICAJCWVsaWYgJ25vIHBhcmVjZSBxdWUgaGF5YSB1bmEnIGluIE8wMDB4MDAwME9PTzAwMFsnbWVuc2FqZSddOgogICAgICAgIAkJCU8wMDB4MDAwME8wMDAwMD1PMDAweDAwMDBPMDAwMDArMQogICAgICAgIAkJZWxzZToKICAgICAgICAJCQlpZiAnLm1wZCcgaW4gTzAwMHgwMDAwT09PMDAwWydtZW5zYWplJ106CiAgICAgICAgCQkJCU9PMDB4MDBPTzAwMDAwMD1PMDAweDAwMDBPT08wMDBbJ21lbnNhamUnXS5zcGxpdCgnLm1wZDwvZGl2PicpCiAgICAgICAgCQkJCU9PMDB4ME9PMDAwMDAwMD1PTzAweDAwT08wMDAwMDBbMF0uc3BsaXQoJz4nKQogICAgICAgIAkJCQlPMDAweDAwMDAwMDBPTzAuZXhlY3V0ZSgiSU5TRVJUIElOVE8gYTNsaW5rcyBWQUxVRVMgKCciK08wMDB4MDAwTzAwMDAwMCsiJywgJyIrT08wMHgwT08wMDAwMDAwWy0xXSsnLm1wZCcrIicsICdPMDAweE9PT09PT09PT08nKTsiKQogICAgICAgIAkJCQlPMDAweDAwMDAwME9PMDAuY29tbWl0KCkKICAgICAgICAJCQkJTzAwMHgwME8wMDAwMDAwLmFwcGVuZCh7J08wMDB4MDBPTzAwMDAwMCc6T08wMHgwT08wMDAwMDAwWy0xXSsnLm1wZCcsJ08wMDB4MDAwMDAwMDBPTyc6J08wMDB4T09PT09PT09PTyd9KQogICAgICAgIAkJCWlmICcuZjRtJyBpbiBPMDAweDAwMDBPT08wMDBbJ21lbnNhamUnXToKICAgICAgICAJCQkJT08wMHgwME9PMDAwMDAwPU8wMDB4MDAwME9PTzAwMFsnbWVuc2FqZSddLnNwbGl0KCcuZjRtPC9kaXY+JykKICAgICAgICAJCQkJT08wMHgwT08wMDAwMDAwPU9PMDB4MDBPTzAwMDAwMFswXS5zcGxpdCgnPicpCiAgICAgICAgCQkJCU8wMDB4MDAwMDAwME9PMC5leGVjdXRlKCJJTlNFUlQgSU5UTyBhM2xpbmtzIFZBTFVFUyAoJyIrTzAwMHgwMDBPMDAwMDAwKyInLCAnIitPTzAweDBPTzAwMDAwMDBbLTFdKycuZjRtJysiJywgJ09PMDB4MDAwT08wMDAwMCcpOyIpCiAgICAgICAgCQkJCU8wMDB4MDAwMDAwT08wMC5jb21taXQoKQogICAgICAgIAkJCQlPMDAweDAwTzAwMDAwMDAuYXBwZW5kKHsnTzAwMHgwME9PMDAwMDAwJzpPTzAweDBPTzAwMDAwMDBbLTFdKycuZjRtJywnTzAwMHgwMDAwMDAwME9PJzonT08wMHgwMDBPTzAwMDAwJ30pCiAgICAgICAgCQkJaWYgJy5tM3U4JyBpbiBPMDAweDAwMDBPT08wMDBbJ21lbnNhamUnXToKICAgICAgICAJCQkJT08wMHgwME9PMDAwMDAwPU8wMDB4MDAwME9PTzAwMFsnbWVuc2FqZSddLnNwbGl0KCcubTN1OCcpCiAgICAgICAgCQkJCU9PMDB4ME9PMDAwMDAwMD1PTzAweDAwT08wMDAwMDBbMF0uc3BsaXQoJ1wnJykKICAgICAgICAJCQkJT08wMHhPTzAwMDAwMDAwPU9PMDB4MDBPTzAwMDAwMFsxXS5zcGxpdCgnXCcnKQogICAgICAgIAkJCQlPMDAweDAwMDAwT09PT089T08wMHgwT08wMDAwMDAwWy0xXSsnLm0zdTgnK09PMDB4T08wMDAwMDAwMFswXQogICAgICAgIAkJCQlPMDAweE9PT08wMDAwMDA9TzAwMHgwMDAwME9PT09PLnJlcGxhY2UoJ2RybScsJycpCiAgICAgICAgCQkJCU8wMDB4MDAwMDAwME9PMC5leGVjdXRlKCJJTlNFUlQgSU5UTyBhM2xpbmtzIFZBTFVFUyAoJyIrTzAwMHgwMDBPMDAwMDAwKyInLCAnIitPMDAweE9PT08wMDAwMDArIicsICdPMDAweDAwT09PT09PT08nKTsiKQogICAgICAgIAkJCQlPMDAweDAwMDAwME9PMDAuY29tbWl0KCkKICAgICAgICAJCQkJTzAwMHgwME8wMDAwMDAwLmFwcGVuZCh7J08wMDB4MDBPTzAwMDAwMCc6TzAwMHhPT09PMDAwMDAwLCdPMDAweDAwMDAwMDAwT08nOidPMDAweDAwT09PT09PT08nfSkKICAgICAgICAJCQllbHNlOgogICAgICAgIAkJCQlPMDAweDBPMDAwMDAwMDA9MAogICAgICAgIAkJCQl3aGlsZSBUcnVlOgogICAgICAgIAkJCQkJaWYgTzAwMHgwTzAwMDAwMDAwPT0zOgogICAgICAgIAkJCQkJCWJyZWFrCiAgICAgICAgCQkJCQlPTzAweDAwT08wMDAwMDA9TzAwMHgwMDAwT09PMDAwWydtZW5zYWplJ10uc3BsaXQoJzxhIGhyZWY9IicpCiAgICAgICAgCQkJCQlPTzAweDBPTzAwMDAwMDA9T08wMHgwME9PMDAwMDAwWzNdLnNwbGl0KCciJykKICAgICAgICAJCQkJCU8wMDB4MDAwME9PT09PMD17J1NlYy1GZXRjaC1Nb2RlJzonY29ycycsJ09yaWdpbic6J2h0dHBzOi8vZWxqYXZpZXJvLmNvbScsJ0FjY2VwdC1MYW5ndWFnZSc6J2VzLUVTLGVzO3E9MC45JywnWC1SZXF1ZXN0ZWQtV2l0aCc6J1hNTEh0dHBSZXF1ZXN0JywnQ29ubmVjdGlvbic6J2tlZXAtYWxpdmUnLCdQcmFnbWEnOiduby1jYWNoZScsJ1VzZXItQWdlbnQnOidNb3ppbGxhLzUuMCAoWDExOyBMaW51eCB4ODZfNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS83Ny4wLjM4NjUuMTIwIFNhZmFyaS81MzcuMzYnLCdDb250ZW50LVR5cGUnOidhcHBsaWNhdGlvbi94LXd3dy1mb3JtLXVybGVuY29kZWQ7IGNoYXJzZXQ9VVRGLTgnLCdBY2NlcHQnOicqLyonLCdDYWNoZS1Db250cm9sJzonbm8tY2FjaGUnLCdSZWZlcmVyJzpPTzAweDBPTzAwMDAwMDBbMF0sJ1NlYy1GZXRjaC1TaXRlJzonc2FtZS1vcmlnaW4nfQogICAgICAgIAkJCQkJTzAwMHgwME9PT09PMDAwPXVybGxpYi51cmxlbmNvZGUoeyd1cmxfbm90aWNpYSc6TzAwMHgwMDBPMDAwMDAwLCdzdWJtaXRfZW52aWFyX3VybCc6J29rJywnY3VycmVudF91cmwnOk9PMDB4ME9PMDAwMDAwMFswXX0pCiAgICAgICAgCQkJCQlPMDAweDAwME9PT08wMDA9dXJsbGliMi5SZXF1ZXN0KCJodHRwczovL2VsamF2aWVyby5jb20vZGVzY2FyZ2FydmlkZW9zZGVsYXRlbGUvaW5kZXgucGhwIixkYXRhPU8wMDB4MDBPT09PTzAwMCxoZWFkZXJzPU8wMDB4MDAwME9PT09PMCkKICAgICAgICAJCQkJCU8wMDB4TzAwMDAwMDAwMD1qc29uLmxvYWRzKHVybGxpYjIudXJsb3BlbihPMDAweDAwME9PT08wMDApLnJlYWQoKSkKICAgICAgICAJCQkJCWlmICcubTN1OCcgbm90IGluIE8wMDB4TzAwMDAwMDAwMFsnbWVuc2FqZSddOgogICAgICAgIAkJCQkJCU8wMDB4ME8wMDAwMDAwMD1PMDAweDBPMDAwMDAwMDArMQogICAgICAgIAkJCQkJCXhibWMuc2xlZXAocmFuZG9tLnJhbmRpbnQoMTAwLDM1MCkpCiAgICAgICAgCQkJCQllbHNlOgogICAgICAgIAkJCQkJCU9PMDB4MDBPTzAwMDAwMD1PMDAweE8wMDAwMDAwMDBbJ21lbnNhamUnXS5zcGxpdCgnLm0zdTgnKQogICAgICAgIAkJCQkJCU9PMDB4ME9PMDAwMDAwMD1PTzAweDAwT08wMDAwMDBbMF0uc3BsaXQoJ1wnJykKICAgICAgICAJCQkJCQlPTzAweE9PMDAwMDAwMDA9T08wMHgwME9PMDAwMDAwWzFdLnNwbGl0KCdcJycpCiAgICAgICAgCQkJCQkJTzAwMHgwMDAwME9PT09PPU9PMDB4ME9PMDAwMDAwMFstMV0rJy5tM3U4JytPTzAweE9PMDAwMDAwMDBbMF0KICAgICAgICAJCQkJCQlPMDAweE9PT08wMDAwMDA9TzAwMHgwMDAwME9PT09PLnJlcGxhY2UoJ2RybScsJycpCiAgICAgICAgCQkJCQkJTzAwMHgwMDAwMDAwT08wLmV4ZWN1dGUoIklOU0VSVCBJTlRPIGEzbGlua3MgVkFMVUVTICgnIitPMDAweDAwME8wMDAwMDArIicsICciK08wMDB4T09PTzAwMDAwMCsiJywgJ08wMDB4MDBPT09PT09PTycpOyIpCiAgICAgICAgCQkJCQkJTzAwMHgwMDAwMDBPTzAwLmNvbW1pdCgpCiAgICAgICAgCQkJCQkJTzAwMHgwME8wMDAwMDAwLmFwcGVuZCh7J08wMDB4MDBPTzAwMDAwMCc6TzAwMHhPT09PMDAwMDAwLCdPMDAweDAwMDAwMDAwT08nOidPMDAweDAwT09PT09PT08nfSkKICAgICAgICAJCQkJCQlicmVhawogICAgICAgIAkJCXJldHVybiBPMDAweDAwTzAwMDAwMDAKICAgICAgICAJCWlmIE8wMDB4MDAwME8wMDAwMD4wOgogICAgICAgIAkJCXhibWMuc2xlZXAocmFuZG9tLnJhbmRpbnQoMTAwLDM1MCkpCiAgICAgICAgCQkJcmV0dXJuIE8wMDB4ME9PT09PMDAwMChPMDAweDAwME8wMDAwMDAsTzAwMHgwMDAwTzAwMDAwKQogICAgICAgIAlleGNlcHQ6CiAgICAgICAgCQlyZXR1cm4gTzAwMHgwT09PT08wMDAwKE8wMDB4MDAwTzAwMDAwMCwzKQpPMDAweE9PT09PTzAwMDA9T08wMHgwMDAwMDAwME8wLmdldCgnTzAwMHhPT09PT08wMDAwJyxOb25lKQppZiBPMDAweE9PT09PTzAwMDAgaXMgTm9uZToKICAgIE8wMDB4MDAwT09PTzAwMD11cmxsaWIyLlJlcXVlc3QoJ2h0dHBzOi8vd3d3LmF0cmVzcGxheWVyLmNvbS8nKQogICAgTzAwMHhPT09PTzAwMDAwPXVybGxpYjIudXJsb3BlbihPMDAweDAwME9PT08wMDApLnJlYWQoKQogICAgTzAwMHgwMDAwT09PT09PPVtdCiAgICBPTzAweDAwT08wMDAwMDA9TzAwMHhPT09PTzAwMDAwLnNwbGl0KCdTaXRlTmF2aWdhdGlvbkVsZW1lbnQiLCJuYW1lIjoiJykKICAgIGZvciBPTzAweDAwMDAwMDBPT08gaW4gcmFuZ2UoMSxsZW4oT08wMHgwME9PMDAwMDAwKSk6CiAgICAgICAgT08wMHgwT08wMDAwMDAwPU9PMDB4MDBPTzAwMDAwMFtPTzAweDAwMDAwMDBPT09dLnNwbGl0KCciJykKICAgICAgICBPTzAweE9PMDAwMDAwMDA9T08wMHgwME9PMDAwMDAwW09PMDB4MDAwMDAwME9PT10uc3BsaXQoJywidXJsIjoiJykKICAgICAgICBPTzAweDAwMDAwT08wMDA9T08wMHhPTzAwMDAwMDAwWzFdLnNwbGl0KCciJykKICAgICAgICBPMDAweDAwMDBPT09PT08uYXBwZW5kKHsnTzAwMHgwMDBPT09PT08wJzpPMDAweDAwMDAwME9PTzAoT08wMHgwT08wMDAwMDAwWzBdKSwnTzAwMHgwME9PMDAwMDAwJzpPTzAweDAwMDAwT08wMDBbMF0ucmVwbGFjZSgnXFx1MDAyRicsJy8nKX0pCiAgICBmb3IgT08wMHgwMDAwME8wMDAwIGluIE8wMDB4MDAwME9PT09PTzoKICAgICAgICBPMDAweDAwT08wMDAwMDA9TzAwMHgwT08wMDAwMDAwKHsnTzAwMHhPT09PT08wMDAwJzonTzAwMHgwME9PT09PTzAwJywnTzAwMHgwT09PT09PMDAwJzpPTzAweDAwMDAwTzAwMDBbJ08wMDB4MDAwT09PT09PMCddLCdPTzAweDAwMDAwME9PMDAnOk9PMDB4MDAwMDBPMDAwMFsnTzAwMHgwME9PMDAwMDAwJ119KQogICAgICAgIE9PMDB4MDAwMDAwME9PMD14Ym1jZ3VpLkxpc3RJdGVtKE9PMDB4MDAwMDBPMDAwMFsnTzAwMHgwMDBPT09PT08wJ10saWNvbkltYWdlPU8wMDB4ME9PT09PT09PMCsnL2ljb24ucG5nJykKICAgICAgICBPTzAweDAwMDAwMDBPTzAuc2V0SW5mbyh0eXBlPSJWaWRlbyIsaW5mb0xhYmVscz17InBsb3QiOk9PMDB4MDAwMDBPMDAwMFsnTzAwMHgwMDBPT09PT08wJ119KQogICAgICAgIE9PMDB4MDAwMDAwME9PMC5zZXRBcnQoeydmYW5hcnQnOk8wMDB4ME9PT09PT09PMCsnL2ZhbmFydC5qcGcnfSkKICAgICAgICB4Ym1jcGx1Z2luLmFkZERpcmVjdG9yeUl0ZW0oaGFuZGxlPU8wMDB4MDAwT09PT09PTyx1cmw9TzAwMHgwME9PMDAwMDAwLGxpc3RpdGVtPU9PMDB4MDAwMDAwME9PMCxpc0ZvbGRlcj1UcnVlKQogICAgeGJtY3BsdWdpbi5lbmRPZkRpcmVjdG9yeShPMDAweDAwME9PT09PT08pCmVsaWYgTzAwMHhPT09PT08wMDAwWzBdPT0nTzAwMHgwME9PT09PTzAwJzoKICAgIE8wMDB4MDAwT09PTzAwMD11cmxsaWIyLlJlcXVlc3QoT08wMHgwMDAwMDAwME8wWydPTzAweDAwMDAwME9PMDAnXVswXSkKICAgIE8wMDB4MDAwMDAwT09PTz11cmxsaWIyLnVybG9wZW4oTzAwMHgwMDBPT09PMDAwKS5yZWFkKCkKICAgIE9PMDB4MDBPTzAwMDAwMD1PMDAweDAwMDAwME9PT08uc3BsaXQoJyJyZWRpcmVjdCI6ZmFsc2UsImhyZWYiOiInKQogICAgT08wMHgwT08wMDAwMDAwPU9PMDB4MDBPTzAwMDAwMFsxXS5zcGxpdCgnIicpCiAgICBPTzAweE9PMDAwMDAwMDA9T08wMHgwT08wMDAwMDAwWzBdLnNwbGl0KCdjaGFubmVsXHUwMDJGJykKICAgIE9PMDB4MDAwMDBPTzAwMD1PTzAweE9PMDAwMDAwMDBbMV0uc3BsaXQoJz8nKQogICAgTzAwMHgwMDAwME9PT08wPU9PMDB4MDAwMDBPTzAwMFswXQogICAgT08wMHgwT09PMDAwMDAwPU9PMDB4ME9PMDAwMDAwMFswXS5zcGxpdCgnY2F0ZWdvcnlJZD0nKQogICAgTzAwMHgwMDAwT09PTzAwPU9PMDB4ME9PTzAwMDAwMFsxXQogICAgTzAwMHgwMDBPT09PMDAwPXVybGxpYjIuUmVxdWVzdCgnaHR0cHM6Ly9hcGkuYXRyZXNwbGF5ZXIuY29tL2NsaWVudC92MS9yb3cvc2VhcmNoP2VudGl0eVR5cGU9QVRQRm9ybWF0JnNlY3Rpb25DYXRlZ29yeT10cnVlJm1haW5DaGFubmVsSWQ9JytPMDAweDAwMDAwT09PTzArJyZjYXRlZ29yeUlkPScrTzAwMHgwMDAwT09PTzAwKycmc29ydFR5cGU9QVomc2l6ZT0xMDAmcGFnZT0wJykKICAgIE8wMDB4MDBPT08wMDAwMD1qc29uLmxvYWRzKHVybGxpYjIudXJsb3BlbihPMDAweDAwME9PT08wMDApLnJlYWQoKSkKICAgIE8wMDB4T09PMDAwMDAwMD1bXQogICAgZm9yIE9PMDB4MDAwMDBPMDAwMCBpbiBPMDAweDAwT09PMDAwMDBbJ2l0ZW1Sb3dzJ106CiAgICAgICAgTzAwMHhPT08wMDAwMDAwLmFwcGVuZCh7Ik9PMDB4MDAwT09PMDAwMCI6T08wMHgwMDAwME8wMDAwWydmb3JtYXRJZCddLCJPMDAweDBPT09PT08wMDAiOk8wMDB4MDAwMDAwT09PMChPTzAweDAwMDAwTzAwMDBbJ3RpdGxlJ10pLCJPTzAweDAwMDBPT08wMDAiOk9PMDB4MDAwMDBPMDAwMFsnaW1hZ2UnXVsncGF0aEhvcml6b250YWwnXSwiT08wMHgwMDAwMDBPTzAwIjpPMDAweDAwMDAwME9PTzAoT08wMHgwMDAwME8wMDAwWydsaW5rJ11bJ3VybCddKSwiTzAwMHgwT09PMDAwMDAwIjpPMDAweDAwMDAwME8wMDAoT08wMHgwMDAwME8wMDAwWyd0aXRsZSddKS5sb3dlcigpfSkKICAgIE8wMDB4MDAwT09PMDAwMD1pbnQoTzAwMHgwME9PTzAwMDAwWydwYWdlSW5mbyddWyd0b3RhbFBhZ2VzJ10pCiAgICBpZiBPMDAweDAwME9PTzAwMDA+MDoKICAgICAgICBmb3IgT08wMHgwMDAwMDAwT09PIGluIHJhbmdlKDEsTzAwMHgwMDBPT08wMDAwKToKICAgICAgICAgICAgTzAwMHgwMDBPT09PMDAwPXVybGxpYjIuUmVxdWVzdCgnaHR0cHM6Ly9hcGkuYXRyZXNwbGF5ZXIuY29tL2NsaWVudC92MS9yb3cvc2VhcmNoP2VudGl0eVR5cGU9QVRQRm9ybWF0JnNlY3Rpb25DYXRlZ29yeT10cnVlJm1haW5DaGFubmVsSWQ9JytPMDAweDAwMDAwT09PTzArJyZjYXRlZ29yeUlkPScrTzAwMHgwMDAwT09PTzAwKycmc29ydFR5cGU9QVomc2l6ZT0xMDAmcGFnZT0nK3N0cihPTzAweDAwMDAwMDBPT08pKQogICAgICAgICAgICBPMDAweDAwT09PMDAwMDA9anNvbi5sb2Fkcyh1cmxsaWIyLnVybG9wZW4oTzAwMHgwMDBPT09PMDAwKS5yZWFkKCkpCiAgICAgICAgICAgIGZvciBPTzAweDAwMDAwTzAwMDAgaW4gTzAwMHgwME9PTzAwMDAwWydpdGVtUm93cyddOgogICAgICAgICAgICAgICAgTzAwMHhPT08wMDAwMDAwLmFwcGVuZCh7Ik9PMDB4MDAwT09PMDAwMCI6T08wMHgwMDAwME8wMDAwWydmb3JtYXRJZCddLCJPMDAweDBPT09PT08wMDAiOk8wMDB4MDAwMDAwT09PMChPTzAweDAwMDAwTzAwMDBbJ3RpdGxlJ10pLCJPTzAweDAwMDBPT08wMDAiOk9PMDB4MDAwMDBPMDAwMFsnaW1hZ2UnXVsncGF0aEhvcml6b250YWwnXSwiT08wMHgwMDAwMDBPTzAwIjpPMDAweDAwMDAwME9PTzAoT08wMHgwMDAwME8wMDAwWydsaW5rJ11bJ3VybCddKSwiTzAwMHgwT09PMDAwMDAwIjpPMDAweDAwMDAwME8wMDAoT08wMHgwMDAwME8wMDAwWyd0aXRsZSddKS5sb3dlcigpfSkKICAgIE8wMDB4T09PMDAwMDAwMD1zb3J0ZWQoTzAwMHhPT08wMDAwMDAwLGtleT1sYW1iZGEgaTppWydPMDAweDBPT08wMDAwMDAnXSxyZXZlcnNlPUZhbHNlKQogICAgZm9yIE9PMDB4MDAwMDBPMDAwMCBpbiBPMDAweE9PTzAwMDAwMDA6CiAgICAgICAgTzAwMHgwME9PMDAwMDAwPU8wMDB4ME9PMDAwMDAwMCh7J08wMDB4T09PT09PMDAwMCc6J09PMDB4T09PMDAwMDAwMCcsJ08wMDB4ME9PT09PTzAwMCc6T08wMHgwMDAwME8wMDAwWydPMDAweDBPT09PT08wMDAnXSwnT08wMHgwMDAwMDBPTzAwJzpPTzAweDAwMDAwTzAwMDBbJ09PMDB4MDAwMDAwT08wMCddLCdPTzAweDAwME9PTzAwMDAnOk9PMDB4MDAwMDBPMDAwMFsnT08wMHgwMDBPT08wMDAwJ119KQogICAgICAgIE9PMDB4MDAwMDAwME9PMD14Ym1jZ3VpLkxpc3RJdGVtKE9PMDB4MDAwMDBPMDAwMFsnTzAwMHgwT09PT09PMDAwJ10saWNvbkltYWdlPU9PMDB4MDAwMDBPMDAwMFsnT08wMHgwMDAwT09PMDAwJ10pCiAgICAgICAgT08wMHgwMDAwMDAwT08wLnNldEluZm8odHlwZT0iVmlkZW8iLGluZm9MYWJlbHM9eyJwbG90IjpPTzAweDAwMDAwTzAwMDBbJ08wMDB4ME9PT09PTzAwMCddfSkKICAgICAgICBPTzAweDAwMDAwMDBPTzAuc2V0QXJ0KHsnZmFuYXJ0JzpPTzAweDAwMDAwTzAwMDBbJ09PMDB4MDAwME9PTzAwMCddfSkKICAgICAgICB4Ym1jcGx1Z2luLmFkZERpcmVjdG9yeUl0ZW0oaGFuZGxlPU8wMDB4MDAwT09PT09PTyx1cmw9TzAwMHgwME9PMDAwMDAwLGxpc3RpdGVtPU9PMDB4MDAwMDAwME9PMCxpc0ZvbGRlcj1UcnVlKQogICAgeGJtY3BsdWdpbi5lbmRPZkRpcmVjdG9yeShPMDAweDAwME9PT09PT08pCmVsaWYgTzAwMHhPT09PT08wMDAwWzBdPT0nT08wMHhPT08wMDAwMDAwJzoKICAgIE8wMDB4MDAwT09PTzAwMD11cmxsaWIyLlJlcXVlc3QoJ2h0dHBzOi8vYXBpLmF0cmVzcGxheWVyLmNvbS9jbGllbnQvdjEvcm93L3NlYXJjaD9lbnRpdHlUeXBlPUFUUEVwaXNvZGUmZm9ybWF0SWQ9JytPTzAweDAwMDAwMDAwTzBbJ09PMDB4MDAwT09PMDAwMCddWzBdKycmc2l6ZT0xMDAmcGFnZT0wJykKICAgIE9PMDB4MDAwTzAwMDAwMD11cmxsaWIyLnVybG9wZW4oTzAwMHgwMDBPT09PMDAwKS5yZWFkKCkKICAgIE9PMDB4MDAwME8wMDAwMD1qc29uLmxvYWRzKE9PMDB4MDAwTzAwMDAwMCkKICAgIE9PMDB4MDBPMDAwMDAwMD1bXQogICAgaWYgJ2l0ZW1Sb3dzJyBpbiBPTzAweDAwMDBPMDAwMDA6CiAgICAgICAgZm9yIE9PMDB4MDAwMDBPMDAwMCBpbiBPTzAweDAwMDBPMDAwMDBbJ2l0ZW1Sb3dzJ106CiAgICAgICAgICAgIE9PMDB4MDAwMDAwT09PMD0nJwogICAgICAgICAgICBpZiAndGFnVHlwZScgaW4gT08wMHgwMDAwME8wMDAwOgogICAgICAgICAgICAgICAgT08wMHgwMDAwMDBPT08wPSdbUF0nCiAgICAgICAgICAgIE9PMDB4MDBPMDAwMDAwMC5hcHBlbmQoeyJPMDAweDBPT09PT08wMDAiOk8wMDB4MDAwMDAwT09PMChPTzAweDAwMDAwTzAwMDBbJ3RpdGxlJ10pLCJPTzAweDAwMDAwT09PMDAiOk8wMDB4MDAwMDAwT09PMChPTzAweDAwMDAwTzAwMDBbJ3N1YlRpdGxlJ10pLCJPTzAweDAwMDBPT08wMDAiOk9PMDB4MDAwMDBPMDAwMFsnaW1hZ2UnXVsncGF0aEhvcml6b250YWwnXSwiT08wMHgwMDAwMDBPTzAwIjpPMDAweDAwMDAwME9PTzAoT08wMHgwMDAwME8wMDAwWydsaW5rJ11bJ3VybCddKSwiTzAwMHhPT09PT09PMDAwIjpPTzAweDAwMDAwME9PTzB9KQogICAgICAgIE8wMDB4MDAwT09PMDAwMD1pbnQoT08wMHgwMDAwTzAwMDAwWydwYWdlSW5mbyddWyd0b3RhbFBhZ2VzJ10pCiAgICAgICAgaWYgTzAwMHgwMDBPT08wMDAwPjA6CiAgICAgICAgICAgIGZvciBPTzAweDAwMDAwMDBPT08gaW4gcmFuZ2UoMSxPMDAweDAwME9PTzAwMDApOgogICAgICAgICAgICAgICAgTzAwMHgwMDBPT09PMDAwPXVybGxpYjIuUmVxdWVzdCgnaHR0cHM6Ly9hcGkuYXRyZXNwbGF5ZXIuY29tL2NsaWVudC92MS9yb3cvc2VhcmNoP2VudGl0eVR5cGU9QVRQRXBpc29kZSZmb3JtYXRJZD0nK09PMDB4MDAwMDAwMDBPMFsnT08wMHgwMDBPT08wMDAwJ11bMF0rJyZzaXplPTEwMCZwYWdlPScrc3RyKE9PMDB4MDAwMDAwME9PTykpCiAgICAgICAgICAgICAgICBPTzAweDAwMDBPMDAwMDA9anNvbi5sb2Fkcyh1cmxsaWIyLnVybG9wZW4oTzAwMHgwMDBPT09PMDAwKS5yZWFkKCkpCiAgICAgICAgICAgICAgICBmb3IgT08wMHgwMDAwME8wMDAwIGluIE9PMDB4MDAwME8wMDAwMFsnaXRlbVJvd3MnXToKICAgICAgICAgICAgICAgICAgICBPTzAweDAwMDAwME9PTzA9JycKICAgICAgICAgICAgICAgICAgICBpZiAndGFnVHlwZScgaW4gT08wMHgwMDAwME8wMDAwOgogICAgICAgICAgICAgICAgICAgICAgICBPTzAweDAwMDAwME9PTzA9J1tQXScKICAgICAgICAgICAgICAgICAgICBPTzAweDAwTzAwMDAwMDAuYXBwZW5kKHsiTzAwMHgwT09PT09PMDAwIjpPMDAweDAwMDAwME9PTzAoT08wMHgwMDAwME8wMDAwWyd0aXRsZSddKSwiT08wMHgwMDAwME9PTzAwIjpPMDAweDAwMDAwME9PTzAoT08wMHgwMDAwME8wMDAwWydzdWJUaXRsZSddKSwiT08wMHgwMDAwT09PMDAwIjpPTzAweDAwMDAwTzAwMDBbJ2ltYWdlJ11bJ3BhdGhIb3Jpem9udGFsJ10sIk9PMDB4MDAwMDAwT08wMCI6TzAwMHgwMDAwMDBPT08wKE9PMDB4MDAwMDBPMDAwMFsnbGluayddWyd1cmwnXSksIk8wMDB4T09PT09PTzAwMCI6T08wMHgwMDAwMDBPT08wfSkKICAgICAgICBmb3IgT08wMHgwMDAwME8wMDAwIGluIE9PMDB4MDBPMDAwMDAwMDoKICAgICAgICAgICAgTzAwMHgwME9PMDAwMDAwPU8wMDB4ME9PMDAwMDAwMCh7J08wMDB4T09PT09PMDAwMCc6J09PMDB4ME8wMDAwMDAwMCcsJ08wMDB4ME9PT09PTzAwMCc6T08wMHgwMDAwME8wMDAwWydPMDAweDBPT09PT08wMDAnXSwnT08wMHgwMDAwMDBPTzAwJzpPTzAweDAwMDAwTzAwMDBbJ09PMDB4MDAwMDAwT08wMCddLCdPTzAweDAwMDBPT08wMDAnOk9PMDB4MDAwMDBPMDAwMFsnT08wMHgwMDAwT09PMDAwJ119KQogICAgICAgICAgICBPTzAweDAwMDAwMDBPTzA9eGJtY2d1aS5MaXN0SXRlbShPTzAweDAwMDAwTzAwMDBbJ08wMDB4ME9PT09PTzAwMCddLGljb25JbWFnZT1PTzAweDAwMDAwTzAwMDBbJ09PMDB4MDAwME9PTzAwMCddKQogICAgICAgICAgICBPTzAweDAwMDAwMDBPTzAuc2V0SW5mbyh0eXBlPSJWaWRlbyIsaW5mb0xhYmVscz17InBsb3QiOk9PMDB4MDAwMDBPMDAwMFsnTzAwMHgwT09PT09PMDAwJ119KQogICAgICAgICAgICBPTzAweDAwMDAwMDBPTzAuc2V0QXJ0KHsnZmFuYXJ0JzpPTzAweDAwMDAwTzAwMDBbJ09PMDB4MDAwME9PTzAwMCddfSkKICAgICAgICAgICAgeGJtY3BsdWdpbi5hZGREaXJlY3RvcnlJdGVtKGhhbmRsZT1PMDAweDAwME9PT09PT08sdXJsPU8wMDB4MDBPTzAwMDAwMCxsaXN0aXRlbT1PTzAweDAwMDAwMDBPTzAsaXNGb2xkZXI9VHJ1ZSkKICAgICAgICB4Ym1jcGx1Z2luLmVuZE9mRGlyZWN0b3J5KE8wMDB4MDAwT09PT09PTykKICAgIGVsc2U6CiAgICAgICAgeGJtYy5leGVjdXRlYnVpbHRpbignWEJNQy5Ob3RpZmljYXRpb24oJXMsJXMsJXMsJXMpJyAlICgnTm8gaGF5IHZpZGVvcycsJ05vIHNlIGhhbiBlbmNvbnRyYWRvIHZpZGVvcyBwYXJhIGVzdGUgcHJvZ3JhbWEnLDQwMDAsTzAwMHgwT09PT09PT08wKycvaWNvbi5wbmcnKSkKZWxpZiBPMDAweE9PT09PTzAwMDBbMF09PSdPTzAweDBPMDAwMDAwMDAnOgogICAgT08wMHhPMDAwMDAwMDAwPU8wMDB4ME9PT09PMDAwMCgnaHR0cHM6Ly93d3cuYXRyZXNwbGF5ZXIuY29tJytPTzAweDAwMDAwMDAwTzBbJ09PMDB4MDAwMDAwT08wMCddWzBdLDApCiAgICBPMDAwMHgwME9PMDAwMDA9TzAwMDB4MDAwMDAwMDAwKCdodHRwczovL3d3dy5hdHJlc3BsYXllci5jb20nK09PMDB4MDAwMDAwMDBPMFsnT08wMHgwMDAwMDBPTzAwJ11bMF0pCiAgICBpZiBsZW4oTzAwMDB4MDBPTzAwMDAwKT09MCBhbmQgbGVuKE9PMDB4TzAwMDAwMDAwMCk9PTA6CiAgICAgICAgeGJtYy5leGVjdXRlYnVpbHRpbignWEJNQy5Ob3RpZmljYXRpb24oJXMsJXMsJXMsJXMpJyAlICgnVmlkZW8gbm8gYWNjZXNpYmxlJywiUHVlZGUgcXVlIHNlYSBtdXkgbnVldm8gbyBxdWUgYXVuIG5vIHNlIGhheWEgZW1pdGlkby4gUHJ1ZWJhIG1hcyBhZGVsYW50ZS4iLDE1MDAwLE8wMDB4ME9PT09PT09PMCsnL2ljb24ucG5nJykpCiAgICBlbHNlOgogICAgICAgIGlmIGxlbihPMDAwMHgwME9PMDAwMDApID4gMDoKICAgICAgICAgICAgZm9yIE8wMDAweDAwME8wMDAwMCBpbiByYW5nZSgwLGxlbihPMDAwMHgwME9PMDAwMDApKToKICAgICAgICAgICAgCWlmICcubTN1OCcgaW4gTzAwMDB4MDBPTzAwMDAwW08wMDAweDAwME8wMDAwMF1bJ08wMDAweDAwMDAwME9PMCddOgogICAgICAgICAgICAJCU8wMDB4ME9PT09PT08wMD14Ym1jZ3VpLkxpc3RJdGVtKCdEaXJlY3RvIHwgW0JdJytPTzAweDAwMDAwMDAwTzBbJ08wMDB4ME9PT09PTzAwMCddWzBdKydbL0JdJyxpY29uSW1hZ2U9T08wMHgwMDAwMDAwME8wWydPTzAweDAwMDBPT08wMDAnXVswXSkKICAgICAgICAgICAgCQlPMDAweDBPT09PT09PMDAuc2V0TGFiZWwoJ0RpcmVjdG8gfCBbQl0nK09PMDB4MDAwMDAwMDBPMFsnTzAwMHgwT09PT09PMDAwJ11bMF0rJ1svQl0nKQogICAgICAgICAgICAJCU8wMDB4ME9PT09PT08wMC5zZXRJbmZvKHR5cGU9IlZpZGVvIixpbmZvTGFiZWxzPXsicGxvdCI6T08wMHgwMDAwMDAwME8wWydPMDAweDBPT09PT08wMDAnXVswXSwnVGl0bGUnOk9PMDB4MDAwMDAwMDBPMFsnTzAwMHgwT09PT09PMDAwJ11bMF19KQogICAgICAgICAgICAJCU8wMDB4ME9PT09PT08wMC5zZXRBcnQoeydmYW5hcnQnOk9PMDB4MDAwMDAwMDBPMFsnT08wMHgwMDAwT09PMDAwJ11bMF19KQogICAgICAgICAgICAJCU8wMDB4ME9PT09PT08wMC5zZXRQcm9wZXJ0eSgiSXNQbGF5YWJsZSIsInRydWUiKQogICAgICAgICAgICAJCXhibWNwbHVnaW4uYWRkRGlyZWN0b3J5SXRlbShoYW5kbGU9TzAwMHgwMDBPT09PT09PLHVybD1PMDAwMHgwME9PMDAwMDBbTzAwMDB4MDAwTzAwMDAwXVsnTzAwMDB4MDAwMDAwT08wJ10sbGlzdGl0ZW09TzAwMHgwT09PT09PTzAwLGlzRm9sZGVyPUZhbHNlKQogICAgICAgICAgICAJZWxpZiAnLm1wZCcgaW4gTzAwMDB4MDBPTzAwMDAwW08wMDAweDAwME8wMDAwMF1bJ08wMDAweDAwMDAwME9PMCddOgogICAgICAgICAgICAJCU8wMDB4ME9PT09PT08wMD14Ym1jZ3VpLkxpc3RJdGVtKCdBdXRvIHwgW0JdJytPTzAweDAwMDAwMDAwTzBbJ08wMDB4ME9PT09PTzAwMCddWzBdKydbL0JdJyxpY29uSW1hZ2U9T08wMHgwMDAwMDAwME8wWydPTzAweDAwMDBPT08wMDAnXVswXSkKICAgICAgICAgICAgCQlPMDAweDBPT09PT09PMDAuc2V0TGFiZWwoJ0F1dG8gfCBbQl0nK09PMDB4MDAwMDAwMDBPMFsnTzAwMHgwT09PT09PMDAwJ11bMF0rJ1svQl0nKQogICAgICAgICAgICAJCU8wMDB4ME9PT09PT08wMC5zZXRJbmZvKHR5cGU9IlZpZGVvIixpbmZvTGFiZWxzPXsicGxvdCI6T08wMHgwMDAwMDAwME8wWydPMDAweDBPT09PT08wMDAnXVswXSwnVGl0bGUnOk9PMDB4MDAwMDAwMDBPMFsnTzAwMHgwT09PT09PMDAwJ11bMF19KQogICAgICAgICAgICAJCU8wMDB4ME9PT09PT08wMC5zZXRBcnQoeydmYW5hcnQnOk9PMDB4MDAwMDAwMDBPMFsnT08wMHgwMDAwT09PMDAwJ11bMF19KQogICAgICAgICAgICAJCU8wMDB4ME9PT09PT08wMC5zZXRQcm9wZXJ0eSgiSXNQbGF5YWJsZSIsInRydWUiKQogICAgICAgICAgICAJCU8wMDB4ME9PT09PT08wMC5zZXRQcm9wZXJ0eSgnaW5wdXRzdHJlYW1hZGRvbicsJ2lucHV0c3RyZWFtLmFkYXB0aXZlJykKICAgICAgICAgICAgCQlPMDAweDBPT09PT09PMDAuc2V0UHJvcGVydHkoJ2lucHV0c3RyZWFtLmFkYXB0aXZlLm1hbmlmZXN0X3R5cGUnLCdtcGQnKQogICAgICAgICAgICAJCU8wMDB4ME9PT09PT08wMC5zZXRNaW1lVHlwZSgnYXBwbGljYXRpb24vZGFzaCt4bWwnKQogICAgICAgICAgICAJCU8wMDB4ME9PT09PT08wMC5zZXRDb250ZW50TG9va3VwKEZhbHNlKQogICAgICAgICAgICAJCXhibWNwbHVnaW4uYWRkRGlyZWN0b3J5SXRlbShoYW5kbGU9TzAwMHgwMDBPT09PT09PLHVybD1PMDAwMHgwME9PMDAwMDBbTzAwMDB4MDAwTzAwMDAwXVsnTzAwMDB4MDAwMDAwT08wJ10sbGlzdGl0ZW09TzAwMHgwT09PT09PTzAwLGlzRm9sZGVyPUZhbHNlKQogICAgICAgICAgICAJZWxzZToKICAgICAgICAgICAgCQlPMDAwMHgwMDAwMDBPTzA9TzAwMHgwT08wMDAwMDAwKHsnTzAwMHhPT09PT08wMDAwJzonTzAwMDB4ME9PMDAwMDAwJywnTzAwMDB4T08wMDAwMDAwJzpPMDAwMHgwME9PMDAwMDBbTzAwMDB4MDAwTzAwMDAwXVsnTzAwMDB4MDAwMDAwT08wJ10sJ08wMDAweDAwMDAwME9PTyc6T08wMHgwMDAwMDAwME8wWydPMDAweDBPT09PT08wMDAnXVswXX0pCiAgICAgICAgICAgIAkJTzAwMHgwT09PT09PTzAwPXhibWNndWkuTGlzdEl0ZW0oJ0RpcmVjdG8gfCBbQl0nK09PMDB4MDAwMDAwMDBPMFsnTzAwMHgwT09PT09PMDAwJ11bMF0rJ1svQl0nLGljb25JbWFnZT1PTzAweDAwMDAwMDAwTzBbJ09PMDB4MDAwME9PTzAwMCddWzBdKQogICAgICAgICAgICAJCU8wMDB4ME9PT09PT08wMC5zZXRMYWJlbCgnRGlyZWN0byB8IFtCXScrT08wMHgwMDAwMDAwME8wWydPMDAweDBPT09PT08wMDAnXVswXSsnWy9CXScpCiAgICAgICAgICAgIAkJTzAwMHgwT09PT09PTzAwLnNldEluZm8odHlwZT0iVmlkZW8iLGluZm9MYWJlbHM9eyJwbG90IjpPTzAweDAwMDAwMDAwTzBbJ08wMDB4ME9PT09PTzAwMCddWzBdLCdUaXRsZSc6T08wMHgwMDAwMDAwME8wWydPMDAweDBPT09PT08wMDAnXVswXX0pCiAgICAgICAgICAgIAkJTzAwMHgwT09PT09PTzAwLnNldEFydCh7J2ZhbmFydCc6T08wMHgwMDAwMDAwME8wWydPTzAweDAwMDBPT08wMDAnXVswXX0pCiAgICAgICAgICAgIAkJeGJtY3BsdWdpbi5hZGREaXJlY3RvcnlJdGVtKGhhbmRsZT1PMDAweDAwME9PT09PT08sdXJsPU8wMDAweDAwMDAwME9PMCxsaXN0aXRlbT1PMDAweDBPT09PT09PMDAsaXNGb2xkZXI9VHJ1ZSkKICAgICAgICBPMDAweDBPT09PMDAwMDA9eydPMDAweDAwT09PT09PT08nOicnLCdPMDAweE9PT09PT09PT08nOicnLCdPTzAweDAwME9PMDAwMDAnOicnfQogICAgICAgIGZvciBPTzAweDAwMDBPTzAwMDAgaW4gT08wMHhPMDAwMDAwMDAwOgogICAgICAgICAgICBpZiBPTzAweDAwMDBPTzAwMDBbJ08wMDB4MDAwMDAwMDBPTyddPT0nTzAwMHgwME9PT09PT09PJzoKICAgICAgICAgICAgICAgIE8wMDB4ME9PT08wMDAwMFsnTzAwMHgwME9PT09PT09PJ109T08wMHgwMDAwT08wMDAwWydPMDAweDAwT08wMDAwMDAnXQogICAgICAgICAgICBpZiBPTzAweDAwMDBPTzAwMDBbJ08wMDB4MDAwMDAwMDBPTyddPT0nTzAwMHhPT09PT09PT09PJzoKICAgICAgICAgICAgICAgIE8wMDB4ME9PT08wMDAwMFsnTzAwMHhPT09PT09PT09PJ109T08wMHgwMDAwT08wMDAwWydPMDAweDAwT08wMDAwMDAnXQogICAgICAgICAgICBpZiBPTzAweDAwMDBPTzAwMDBbJ08wMDB4MDAwMDAwMDBPTyddPT0nT08wMHgwMDBPTzAwMDAwJzoKICAgICAgICAgICAgICAgIE8wMDB4ME9PT08wMDAwMFsnT08wMHgwMDBPTzAwMDAwJ109T08wMHgwMDAwT08wMDAwWydPMDAweDAwT08wMDAwMDAnXQogICAgICAgIGlmIE8wMDB4ME9PT08wMDAwMFsnTzAwMHgwME9PT09PT09PJ10hPScnOgogICAgICAgICAgICBPMDAweDBPT09PT09PMDA9eGJtY2d1aS5MaXN0SXRlbSgnRGlyZWN0byB8IFtCXScrT08wMHgwMDAwMDAwME8wWydPMDAweDBPT09PT08wMDAnXVswXSsnWy9CXScsaWNvbkltYWdlPU9PMDB4MDAwMDAwMDBPMFsnT08wMHgwMDAwT09PMDAwJ11bMF0pCiAgICAgICAgICAgIE8wMDB4ME9PT09PT08wMC5zZXRMYWJlbCgnRGlyZWN0byB8IFtCXScrT08wMHgwMDAwMDAwME8wWydPMDAweDBPT09PT08wMDAnXVswXSsnWy9CXScpCiAgICAgICAgICAgIE8wMDB4ME9PT09PT08wMC5zZXRJbmZvKHR5cGU9IlZpZGVvIixpbmZvTGFiZWxzPXsicGxvdCI6T08wMHgwMDAwMDAwME8wWydPMDAweDBPT09PT08wMDAnXVswXSwnVGl0bGUnOk9PMDB4MDAwMDAwMDBPMFsnTzAwMHgwT09PT09PMDAwJ11bMF19KQogICAgICAgICAgICBPMDAweDBPT09PT09PMDAuc2V0QXJ0KHsnZmFuYXJ0JzpPTzAweDAwMDAwMDAwTzBbJ09PMDB4MDAwME9PTzAwMCddWzBdfSkKICAgICAgICAgICAgTzAwMHgwT09PT09PTzAwLnNldFByb3BlcnR5KCJJc1BsYXlhYmxlIiwidHJ1ZSIpCiAgICAgICAgICAgIHhibWNwbHVnaW4uYWRkRGlyZWN0b3J5SXRlbShoYW5kbGU9TzAwMHgwMDBPT09PT09PLHVybD1PMDAweDBPT09PMDAwMDBbJ08wMDB4MDBPT09PT09PTyddLGxpc3RpdGVtPU8wMDB4ME9PT09PT08wMCxpc0ZvbGRlcj1GYWxzZSkKICAgICAgICBpZiBPMDAweDBPT09PMDAwMDBbJ08wMDB4T09PT09PT09PTyddIT0nJzoKICAgICAgICAgICAgTzAwMHgwT09PT09PTzAwPXhibWNndWkuTGlzdEl0ZW0oJ0F1dG8gfCBbQl0nK09PMDB4MDAwMDAwMDBPMFsnTzAwMHgwT09PT09PMDAwJ11bMF0rJ1svQl0nLGljb25JbWFnZT1PTzAweDAwMDAwMDAwTzBbJ09PMDB4MDAwME9PTzAwMCddWzBdKQogICAgICAgICAgICBPMDAweDBPT09PT09PMDAuc2V0TGFiZWwoJ0F1dG8gfCBbQl0nK09PMDB4MDAwMDAwMDBPMFsnTzAwMHgwT09PT09PMDAwJ11bMF0rJ1svQl0nKQogICAgICAgICAgICBPMDAweDBPT09PT09PMDAuc2V0SW5mbyh0eXBlPSJWaWRlbyIsaW5mb0xhYmVscz17InBsb3QiOk9PMDB4MDAwMDAwMDBPMFsnTzAwMHgwT09PT09PMDAwJ11bMF0sJ1RpdGxlJzpPTzAweDAwMDAwMDAwTzBbJ08wMDB4ME9PT09PTzAwMCddWzBdfSkKICAgICAgICAgICAgTzAwMHgwT09PT09PTzAwLnNldEFydCh7J2ZhbmFydCc6T08wMHgwMDAwMDAwME8wWydPTzAweDAwMDBPT08wMDAnXVswXX0pCiAgICAgICAgICAgIE8wMDB4ME9PT09PT08wMC5zZXRQcm9wZXJ0eSgiSXNQbGF5YWJsZSIsInRydWUiKQogICAgICAgICAgICBPMDAweDBPT09PT09PMDAuc2V0UHJvcGVydHkoJ2lucHV0c3RyZWFtYWRkb24nLCdpbnB1dHN0cmVhbS5hZGFwdGl2ZScpCiAgICAgICAgICAgIE8wMDB4ME9PT09PT08wMC5zZXRQcm9wZXJ0eSgnaW5wdXRzdHJlYW0uYWRhcHRpdmUubWFuaWZlc3RfdHlwZScsJ21wZCcpCiAgICAgICAgICAgIE8wMDB4ME9PT09PT08wMC5zZXRNaW1lVHlwZSgnYXBwbGljYXRpb24vZGFzaCt4bWwnKQogICAgICAgICAgICBPMDAweDBPT09PT09PMDAuc2V0Q29udGVudExvb2t1cChGYWxzZSkKICAgICAgICAgICAgeGJtY3BsdWdpbi5hZGREaXJlY3RvcnlJdGVtKGhhbmRsZT1PMDAweDAwME9PT09PT08sdXJsPU8wMDB4ME9PT08wMDAwMFsnTzAwMHhPT09PT09PT09PJ10sbGlzdGl0ZW09TzAwMHgwT09PT09PTzAwLGlzRm9sZGVyPUZhbHNlKQogICAgICAgIGlmIE8wMDB4ME9PT08wMDAwMFsnT08wMHgwMDBPTzAwMDAwJ10hPScnOgogICAgICAgICAgICBPMDAweDAwT09PTzAwMDA9cmVxdWVzdHMuZ2V0KE8wMDB4ME9PT08wMDAwMFsnT08wMHgwMDBPTzAwMDAwJ10pLnRleHQKICAgICAgICAgICAgaWYgJ2JpdHJhdGU9IicgaW4gTzAwMHgwME9PT08wMDAwOgogICAgICAgICAgICAgICAgT08wMHgwMDAwMDAwMDAwPVtdCiAgICAgICAgICAgICAgICBPTzAweDAwMDAwMDAwT089ZjRtUHJveHlIZWxwZXIoKQogICAgICAgICAgICAgICAgTzAwMHgwME9PT09PT08wLE8wMDB4ME9PT09PT08wMD1PTzAweDAwMDAwMDAwT08ucGxheUY0bUxpbmsoTzAwMHgwT09PTzAwMDAwWydPTzAweDAwME9PMDAwMDAnXSxPTzAweDAwMDAwMDAwTzBbJ08wMDB4ME9PT09PTzAwMCddWzBdLE5vbmUsVHJ1ZSwwLEZhbHNlLCcnLCdIRFMnLFRydWUsTm9uZSwnJywnJyxPTzAweDAwMDAwMDAwTzBbJ09PMDB4MDAwME9PTzAwMCddWzBdKQogICAgICAgICAgICAgICAgTzAwMHgwT09PT09PTzAwLnNldFByb3BlcnR5KCJJc1BsYXlhYmxlIiwidHJ1ZSIpCiAgICAgICAgICAgICAgICBPTzAweDBPTzAwMDAwMDA9TzAwMHgwME9PT08wMDAwLnNwbGl0KCdiaXRyYXRlPSInKQogICAgICAgICAgICAgICAgT08wMHgwMDAwMDAwTzAwPU8wMDB4ME9PT09PT08wMC5nZXRMYWJlbCgpLmRlY29kZSgndXRmOCcpCiAgICAgICAgICAgICAgICBmb3IgT08wMHgwME9PTzAwMDAwIGluIHJhbmdlKDEsbGVuKE9PMDB4ME9PMDAwMDAwMCkpOgogICAgICAgICAgICAgICAgICAgIE9PMDB4T08wMDAwMDAwMD1PTzAweDBPTzAwMDAwMDBbT08wMHgwME9PTzAwMDAwXS5zcGxpdCgnIicpCiAgICAgICAgICAgICAgICAgICAgT08wMHgwMDAwMDAwMDAwLmFwcGVuZCh7J09PMDB4MDAwMDAwTzAwMCc6aW50KE9PMDB4T08wMDAwMDAwMFswXSl9KQogICAgICAgICAgICAgICAgT08wMHgwMDAwMDAwMDAwPXNvcnRlZChPTzAweDAwMDAwMDAwMDAsa2V5PWxhbWJkYSBPTzAweDAwT09PMDAwMDA6T08wMHgwME9PTzAwMDAwWydPTzAweDAwMDAwME8wMDAnXSxyZXZlcnNlPVRydWUpCiAgICAgICAgICAgICAgICBmb3IgT08wMHgwMDAwMDAwMDBPIGluIE9PMDB4MDAwMDAwMDAwMDoKICAgICAgICAgICAgICAgICAgICBPMDAweDBPT09PT09PMDAuc2V0TGFiZWwoJ0Y0TSB8ICcrc3RyKE9PMDB4MDAwMDAwMDAwT1snT08wMHgwMDAwMDBPMDAwJ10pKycga2JwcyB8IFtCXScrT08wMHgwMDAwMDAwTzAwKydbL0JdJykKICAgICAgICAgICAgICAgICAgICBPMDAweDBPT09PT09PMDAuc2V0SW5mbyh0eXBlPSJWaWRlbyIsaW5mb0xhYmVscz17InBsb3QiOk9PMDB4MDAwMDAwMDBPMFsnTzAwMHgwT09PT09PMDAwJ11bMF0sJ1RpdGxlJzpPTzAweDAwMDAwMDAwTzBbJ08wMDB4ME9PT09PTzAwMCddWzBdfSkKICAgICAgICAgICAgICAgICAgICBPMDAweDBPT09PT09PMDAuc2V0QXJ0KHsnZmFuYXJ0JzpPTzAweDAwMDAwMDAwTzBbJ09PMDB4MDAwME9PTzAwMCddWzBdfSkKICAgICAgICAgICAgICAgICAgICBPMDAweDBPT09PT09PMDAuc2V0UHJvcGVydHkoIklzUGxheWFibGUiLCJ0cnVlIikKICAgICAgICAgICAgICAgICAgICB4Ym1jcGx1Z2luLmFkZERpcmVjdG9yeUl0ZW0oaGFuZGxlPU8wMDB4MDAwT09PT09PTyx1cmw9TzAwMHgwME9PT09PT08wLnJlcGxhY2UoJ21heGJpdHJhdGU9MCcsJ21heGJpdHJhdGU9JytzdHIoT08wMHgwMDAwMDAwMDBPWydPTzAweDAwMDAwME8wMDAnXSkpLGxpc3RpdGVtPU8wMDB4ME9PT09PT08wMCxpc0ZvbGRlcj1GYWxzZSkKICAgICAgICB4Ym1jcGx1Z2luLmVuZE9mRGlyZWN0b3J5KE8wMDB4MDAwT09PT09PTykKZWxpZiBPMDAweE9PT09PTzAwMDBbMF09PSdPMDAwMHgwT08wMDAwMDAnOgogICAgTzAwMDB4MDAwME9PMDAwPXhibWNndWkuTGlzdEl0ZW0oT08wMHgwMDAwMDAwME8wWydPMDAwMHgwMDAwMDBPT08nXVswXSkKICAgIE8wMDAweDAwMDAwT08wMD0nJwogICAgaWYgJ2dhbW92aWRlbycgaW4gT08wMHgwMDAwMDAwME8wWydPMDAwMHhPTzAwMDAwMDAnXVswXToKICAgICAgICBPMDAwMHgwMDAwME9PTzA9J01vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjApIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS83My4wLjM2ODMuMTAzIFNhZmFyaS81MzcuMzYnCiAgICAgICAgTzAwMDB4MDAwME9PTzAwPXJlcXVlc3RzLnNlc3Npb24oKQogICAgICAgIE8wMDAweDAwME9PTzAwMD1PMDAwMHgwMDAwT09PMDAuZ2V0KE9PMDB4MDAwMDAwMDBPMFsnTzAwMDB4T08wMDAwMDAwJ11bMF0saGVhZGVycz17J1VzZXItQWdlbnQnOk8wMDAweDAwMDAwT09PMH0sdmVyaWZ5PUZhbHNlKQogICAgICAgIE8wMDAweDAwT09PMDAwMD1PMDAwMHgwMDAwT09PMDAuZ2V0KE9PMDB4MDAwMDAwMDBPMFsnTzAwMDB4T08wMDAwMDAwJ11bMF0saGVhZGVycz17J1VzZXItQWdlbnQnOk8wMDAweDAwMDAwT09PMH0sdmVyaWZ5PUZhbHNlKQogICAgICAgIE8wMDAweE9PTzAwMDAwMD1yZS5maW5kYWxsKCdqYXZhc2NyaXB0Lio/KGV2YWxcKGZ1bmN0aW9uXChwLGEsYyxrLGUsZC4qKScsTzAwMDB4MDBPT08wMDAwLnRleHQpWzBdCiAgICAgICAgTzAwMDB4ME9PTzAwMDAwPWpzdW5wYWNrLnVucGFjayhPMDAwMHhPT08wMDAwMDApCiAgICAgICAgTzAwMDB4MDAwMDBPT09PPXJlLmZpbmRhbGwoJyg/cylzb3VyY2VzLio/ZmlsZTpccyoiKGh0dHAuKj8pIicsTzAwMDB4ME9PTzAwMDAwKVswXSsnfFVzZXItQWdlbnQ9JytPMDAwMHgwMDAwME9PTzAKICAgICAgICB4Ym1jLlBsYXllcigpLnBsYXkoTzAwMDB4MDAwMDBPT09PLE8wMDAweDAwMDBPTzAwMCkKICAgIGVsc2U6CiAgICAgICAgdHJ5OgogICAgICAgICAgICBPMDAwMHgwMDAwME9PMDA9dXJscmVzb2x2ZXIucmVzb2x2ZShPTzAweDAwMDAwMDAwTzBbJ08wMDAweE9PMDAwMDAwMCddWzBdKQogICAgICAgIGV4Y2VwdDoKICAgICAgICAgICAgcGFzcwogICAgICAgIGlmIE8wMDAweDAwMDAwT08wMD09Jycgb3IgTzAwMDB4MDAwMDBPTzAwPT1GYWxzZToKICAgICAgICAgICAgdHJ5OgogICAgICAgICAgICAgICAgTzAwMDB4MDAwMDBPTzAwPXJlc29sdmV1cmwucmVzb2x2ZShPTzAweDAwMDAwMDAwTzBbJ08wMDAweE9PMDAwMDAwMCddWzBdKQogICAgICAgICAgICBleGNlcHQ6CiAgICAgICAgICAgICAgICBwYXNzCiAgICAgICAgaWYgTzAwMDB4MDAwMDBPTzAwIT0nJyBhbmQgTzAwMDB4MDAwMDBPTzAwIT1GYWxzZToKICAgICAgICAgICAgeGJtYy5QbGF5ZXIoKS5wbGF5KE8wMDAweDAwMDAwT08wMCxPMDAwMHgwMDAwT08wMDAp'))