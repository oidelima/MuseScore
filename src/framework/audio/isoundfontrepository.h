/*
 * SPDX-License-Identifier: GPL-3.0-only
 * MuseScore-CLA-applies
 *
 * MuseScore
 * Music Composition & Notation
 *
 * Copyright (C) 2021 MuseScore BVBA and others
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3 as
 * published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */
#ifndef MU_AUDIO_ISOUNDFONTREPOSITORY_H
#define MU_AUDIO_ISOUNDFONTREPOSITORY_H

#include "modularity/imoduleinterface.h"

#include "types/ret.h"
#include "async/notification.h"

#include "soundfonttypes.h"

namespace mu::audio {
class ISoundFontRepository : MODULE_EXPORT_INTERFACE
{
    INTERFACE_ID(ISoundFontRepository)

public:
    virtual ~ISoundFontRepository() = default;

    virtual const synth::SoundFontPaths& soundFontPaths() const = 0;
    virtual const synth::SoundFontsMap& soundFonts() const = 0;
    virtual async::Notification soundFontsChanged() const = 0;

    virtual mu::Ret addSoundFont(const synth::SoundFontPath& path) = 0;
};
}

#endif // MU_AUDIO_ISOUNDFONTREPOSITORY_H
