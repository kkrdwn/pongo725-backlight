# Axioo Pongo 725 backlight keyboard for linux
A simple and portable control application for the Axioo Pongo 725 laptop running on Linux distributions such as Arch with Wayland (Hyprland), specifically for managing the RGB backlight keyboard feature.

# Still Prototype
<img width="502" height="435" alt="image" src="https://github.com/user-attachments/assets/84c0d01e-74eb-4415-9192-721c63c4d243" />

## Demo Video
<p align="center">
  <a href="https://youtu.be/VFOXhH-WwCY">
    <img src="https://img.youtube.com/vi/VFOXhH-WwCY/maxresdefault.jpg" />
  </a>
</p>

## Installation
### 1. pacman packages :
```
sudo pacman -S --needed python-gobject gtk3
````
### 2. yay packages :
```
yay -S --needed clevo-drivers-dkms-git
```
### 3. Clone :
```
git clone --depth 1 https://github.com/kkrdwn/axioo_pongo725_backlight.git
```
### 4. Give permission script
```
chmod +x ./main.py
```
### 5. Start app use
```
./main.py
```
