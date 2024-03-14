# ---------------------------------------------------------------------------
# File:   gencert.cmd - generate a certificate fot executable signing.
# Author: Jens Kallup - paule32
#
# Rights: (c) 2024 by kallup non-profit software
#         all rights reserved
#
# only for education, and for non-profit usage !!!
# commercial use ist not allowed.
#
# To create the certificate, copy lines 13, ..., 19 into the clipboard, and
# paste the copied text into powershell console. Press return, and voila:
# you have a self signed certificate into your local certification store.
# ---------------------------------------------------------------------------
New-SelfSignedCertificate `
    -Type Custom          `
    -Subject "CN=kallup non-profit" `
    -KeyUsage DigitalSignature      `
    -FriendlyName "chmFilter"       `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3","2.5.29.19={text}")

$password = ConvertTo-SecureString -String "mypassword" -Force -AsPlainText
Export-PfxCertificate -cert "Cert:\CurrentUser\My\<fingerprint thumb>" -FilePath certificate.pfx -Password $password

# anschließend in der Visual Studio C++ Console:
# signtool sign /f ./certificate.pfx /p mypassword /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 observer.exe
